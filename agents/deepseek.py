import json
import logging

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from tools import ALL_TOOLS, dispatch

logger = logging.getLogger(__name__)

_MAX_TOOL_ITERATIONS = 5


class DeepSeekAgent:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.deepseek_api_key.get_secret_value(),
            base_url=settings.deepseek_base_url,
        )
        self.model = settings.deepseek_model

    def _build_system_prompt(self, user_context: str = "") -> str:
        base = (
            "You are Mogul Manager, an AI assistant built into the Mogul Manager project management platform. "
            "You help users manage workspaces, projects, tasks, plans, and documents.\n\n"

            "TAKE ACTION IMMEDIATELY:\n"
            "When a user asks you to create, update, delete, or change anything — do it right away using the available tools. "
            "Never ask for confirmation or permission before acting. "
            "After completing an action, give a specific confirmation: name the item, include its ID, "
            "and state the outcome clearly (e.g. 'Created task \"Fix login bug\" (id=42) in project Backend, due Friday.'). "
            "If a tool returns an error, report what failed and suggest what the user can do next.\n\n"

            "RESPONSE STYLE:\n"
            "- Be direct and concise. Skip filler phrases like 'Of course!' or 'Sure thing!'.\n"
            "- Lead with results: state what was done before any explanation.\n"
            "- Use short bullet lists when presenting multiple items.\n"
            "- For questions or analysis, answer first — add supporting detail only if it adds value.\n\n"

            "TOOL USE:\n"
            "- Act proactively. If a request implies creating multiple items (e.g. a plan with tasks), do it all.\n"
            "- Chain tool calls within one response to fully complete a request without back-and-forth.\n"
            "- Never output raw tool syntax, JSON blocks, or XML tags in your text response.\n\n"

            "MEMORY:\n"
            "- You have stored memories about this user's preferences, goals, and decisions.\n"
            "- Apply what you know naturally — don't announce that you're using memory, just act on it.\n\n"

            "IDENTITY:\n"
            "Never mention Claude, Anthropic, DeepSeek, or any underlying AI technology. You are Mogul Manager."
        )
        if user_context:
            return f"{base}\n\n--- USER CONTEXT ---\n{user_context}"
        return base

    async def stream_response(
        self,
        messages: list[ChatCompletionMessageParam],
        db: AsyncSession,
        user_context: str = "",
    ):
        history: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self._build_system_prompt(user_context)},
            *messages,
        ]

        for _ in range(_MAX_TOOL_ITERATIONS):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=history,
                tools=ALL_TOOLS,  # type: ignore[arg-type]
                tool_choice="auto",
            )
            choice = response.choices[0]

            if choice.finish_reason != "tool_calls" or not choice.message.tool_calls:
                # Model finished without requesting tools. Yield its response directly
                # to avoid a second redundant API call.
                if choice.message.content:
                    yield {"type": "token", "content": choice.message.content}
                    return
                break

            # Only process standard function-type tool calls
            function_calls = [
                tc for tc in choice.message.tool_calls
                if isinstance(tc, ChatCompletionMessageToolCall)
            ]

            tool_calls_payload = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in function_calls
            ]
            assistant_msg: ChatCompletionMessageParam = {
                "role": "assistant",
                "content": choice.message.content or "",
                "tool_calls": tool_calls_payload,  # type: ignore[typeddict-unknown-key]
            }
            history.append(assistant_msg)

            for tc in function_calls:
                yield {"type": "tool_start", "name": tc.function.name}
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    logger.warning("Tool %s: malformed JSON arguments: %s", tc.function.name, tc.function.arguments)
                    args = {}
                result = await dispatch(tc.function.name, args, db)
                try:
                    parsed_result = json.loads(result)
                    if "error" in parsed_result:
                        logger.warning("Tool %s returned error: %s", tc.function.name, parsed_result["error"])
                except json.JSONDecodeError:
                    pass
                tool_msg: ChatCompletionMessageParam = {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
                history.append(tool_msg)

        # Fallback: stream a final response when the tool loop exhausted its iterations
        # or the model stopped without providing content.
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=history,
            stream=True,
            temperature=0.7,
            max_tokens=2048,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield {"type": "token", "content": delta.content}
