import json
import logging

from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessageParam
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
            "You help users manage their workspaces, projects, and tasks. "
            "You have tools to create, update, list, and search tasks and projects. "
            "Keep responses concise and practical. "
            "When referencing specific items, use their titles. "
            "Never mention Claude, Anthropic, or any underlying AI technology — you are Mogul Manager.\n\n"
            "IMPORTANT — always ask for confirmation before making changes:\n"
            "Before calling any tool that creates, updates, or deletes data, "
            "first explain what you plan to do and ask the user if they want to proceed. "
            "Wait for their approval before executing the tool. "
            "Tools that only read or search data (list, get, search) do not need confirmation.\n\n"
            "CRITICAL — never output raw tool call syntax in your response:\n"
            "When you need to call a tool, use the built-in function calling mechanism — "
            "never write XML-like tags, JSON blocks, or any structured invocation syntax "
            "in your text response. Your reply to the user must always be plain, natural language."
        )
        if user_context:
            return f"{base}\n\n{user_context}"
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
                break

            # Only process standard function-type tool calls
            function_calls = [
                tc for tc in choice.message.tool_calls
                if isinstance(tc, ChatCompletionMessageToolCall)
            ]

            # Append assistant message that contains the tool call requests
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

            # Execute each tool and append its result
            for tc in function_calls:
                yield {"type": "tool_start", "name": tc.function.name}
                args = json.loads(tc.function.arguments)
                result = await dispatch(tc.function.name, args, db)
                parsed_result = json.loads(result)
                if "error" in parsed_result:
                    logger.warning("Tool %s returned error: %s", tc.function.name, parsed_result["error"])
                tool_msg: ChatCompletionMessageParam = {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
                history.append(tool_msg)

        # Stream the final text response
        stream: AsyncStream[ChatCompletionChunk] = await self.client.chat.completions.create(
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
