import json
import logging
import re
from collections.abc import Callable

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from tools import ALL_TOOLS, dispatch
from utils.prompts import PLANNER_SYSTEM, SUGGEST_PROMPTS, build_chat_system_prompt

logger = logging.getLogger(__name__)

_MAX_TOOL_ITERATIONS = settings.max_tool_iterations

_DSML_RE = re.compile(r"<\|+DSML\|+>.*?</\|+DSML\|+tool_calls>", re.DOTALL)
_DSML_OPEN_RE = re.compile(r"<\|+DSML\|+[^>]*>")

_MUTATION_TOOLS = frozenset(
    {
        "create_task",
        "update_task",
        "delete_task",
        "create_project",
        "update_project",
        "delete_project",
        "create_workspace",
        "update_workspace",
        "delete_workspace",
        "store_memory",
        "delete_memory",
        "create_plan",
    }
)


def _strip_dsml(text: str) -> str:
    cleaned = _DSML_RE.sub("", text)
    cleaned = _DSML_OPEN_RE.sub("", cleaned)
    return cleaned


class DeepSeekAgent:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.deepseek_api_key.get_secret_value(),
            base_url=settings.deepseek_base_url,
        )
        self.model = settings.deepseek_model

    def _build_system_prompt(self, user_context: str = "") -> str:
        return build_chat_system_prompt(user_context)

    async def stream_response(
        self,
        messages: list[ChatCompletionMessageParam],
        db: AsyncSession,
        user_context: str = "",
        user_id: int = 0,
        context_builder: Callable | None = None,
    ):
        history: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": self._build_system_prompt(user_context)},
            *messages,
        ]

        _current_user_context = user_context

        for iteration in range(_MAX_TOOL_ITERATIONS):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=history,
                tools=ALL_TOOLS,
                tool_choice="auto",
            )
            choice = response.choices[0]

            if choice.finish_reason != "tool_calls" or not choice.message.tool_calls:
                if choice.message.content:
                    content = _strip_dsml(choice.message.content)
                    if content:
                        yield {"type": "token", "content": content}
                    return
                break

            function_calls = [
                tc
                for tc in choice.message.tool_calls
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
                "tool_calls": tool_calls_payload,
            }
            history.append(assistant_msg)

            had_mutation = False
            for tc in function_calls:
                yield {"type": "tool_start", "name": tc.function.name}
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    logger.warning(
                        "Tool %s: malformed JSON arguments: %s",
                        tc.function.name,
                        tc.function.arguments,
                    )
                    args = {}
                result = await dispatch(tc.function.name, args, db, user_id)
                try:
                    parsed_result = json.loads(result)
                    if "error" in parsed_result:
                        logger.warning(
                            "Tool %s returned error: %s",
                            tc.function.name,
                            parsed_result["error"],
                        )
                    elif tc.function.name in _MUTATION_TOOLS:
                        had_mutation = True
                except json.JSONDecodeError:
                    pass
                tool_msg: ChatCompletionMessageParam = {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
                history.append(tool_msg)

            if had_mutation and context_builder and user_id:
                try:
                    _current_user_context = await context_builder(user_id, db)
                    history[0] = {
                        "role": "system",
                        "content": self._build_system_prompt(_current_user_context),
                    }
                except Exception as exc:
                    logger.warning("Context refresh failed: %s", exc)

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
                content = _strip_dsml(delta.content)
                if content:
                    yield {"type": "token", "content": content}

    async def decompose(
        self,
        goal: str,
        research: str = "",
        existing_tasks: list[dict] | None = None,
    ) -> list[dict]:
        parts: list[str] = []
        if research:
            parts.append(research)
        if existing_tasks:
            task_lines = "\n".join(
                f"  - id={t['id']} | {t['title']} | status={t['status']} | priority={t['priority']}"
                for t in existing_tasks
            )
            parts.append(f"Existing tasks in this project:\n{task_lines}")
        parts.append(f"Goal: {goal}")
        user_content = "\n\n".join(parts)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PLANNER_SYSTEM},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.3,
                max_tokens=4096,
            )
            raw = response.choices[0].message.content or "{}"
            raw = (
                raw.strip()
                .removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
            data = json.loads(raw)
            steps = data.get("steps", [])
            if not isinstance(steps, list) or not steps:
                raise ValueError("Empty steps list")
            return steps[:30]
        except Exception as exc:
            logger.warning("Plan decomposition failed: %s", exc)
            return [
                {
                    "title": goal,
                    "description": None,
                    "priority": "medium",
                    "depends_on": [],
                    "task": {
                        "action": "create",
                        "title": goal,
                        "description": None,
                        "priority": "medium",
                    },
                }
            ]

    async def suggest_field(self, context_type: str, title: str, field: str) -> str:
        system = SUGGEST_PROMPTS.get(context_type, {}).get(field)
        if not system:
            system = (
                f"Generate a concise, professional {field} for a {context_type} "
                f"named '{title}'. 2–3 sentences, plain prose, no markdown."
            )
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"Name: {title}"},
                ],
                temperature=0.65,
                max_tokens=220,
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as exc:
            logger.warning("Field suggestion failed: %s", exc)
            return ""
