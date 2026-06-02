import json
import logging

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion_message_tool_call import (
    ChatCompletionMessageToolCall,
)
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from tools import ALL_TOOLS, dispatch

logger = logging.getLogger(__name__)

_MAX_TOOL_ITERATIONS = 5


# ── Planner prompt (used by decompose()) ─────────────────────────────────────
_PLANNER_SYSTEM_PROMPT = """\
You are a project planning AI embedded in a project management tool. Break down a goal into a clear, ordered sequence of 3–8 concrete, actionable steps.

Return JSON ONLY — no markdown, no explanation:
{
  "steps": [
    {
      "title": "Verb-led action title (5–8 words)",
      "description": "What needs to happen and what done looks like (1–3 sentences)",
      "priority": "low|medium|high|urgent",
      "depends_on": [0, 1]
    }
  ]
}

Rules:
- 3–8 steps, ordered from first to last
- depends_on lists zero-based indices of steps that must complete before this one starts; the first step never has dependencies
- Each step description must include a clear completion condition — what does "done" look like?
- Titles start with an action verb: Research, Draft, Design, Implement, Review, Deploy, Validate, Set up, Configure, Test
- Size steps for a single person to complete in hours to a few days — not vague epics, not micro-tasks
- Assign priority based on how blocking the step is and how time-sensitive it is

Using project context (when provided):
- If "Project context" is present in the goal, read the project's name, status, description and existing tasks carefully
- Do NOT create steps for work already captured in existing tasks — complement them, not duplicate
- Reflect the project's current state: if tasks are in_progress, the plan should pick up from where work stands
- If the project description reveals a domain or technology, make steps specific to it (e.g. "Set up React Router" not "Set up routing")
- Treat existing in_progress or review tasks as context for what is already underway; plan steps should logically follow or parallel them\
"""

# ── Field suggestion prompts (used by suggest_field()) ───────────────────────
_SUGGEST_PROMPTS: dict[str, dict[str, str]] = {
    "workspace": {
        "description": (
            "You are a project management assistant helping users write professional workspace descriptions. "
            "A workspace groups related projects and teams under a shared goal or domain. "
            "Write exactly 2–3 sentences in plain prose that cover: "
            "(1) the workspace's core purpose and domain, "
            "(2) the type of work or projects it houses, "
            "(3) the team or stakeholders it serves. "
            "No bullet points, no markdown, no filler openers like 'This workspace is designed to...'. "
            "Start directly with what the workspace does or represents."
        ),
    },
    "project": {
        "description": (
            "You are a project management assistant helping users write clear project descriptions. "
            "Write exactly 2–3 sentences in plain prose that cover: "
            "(1) what the project delivers or solves, "
            "(2) who it is for or who benefits from it, "
            "(3) what a successful outcome looks like. "
            "No bullet points, no markdown, no filler openers. "
            "Start directly with what the project is or does."
        ),
    },
    "task": {
        "description": (
            "You are a project management assistant helping users write actionable task descriptions. "
            "Write exactly 2–3 sentences in plain prose that cover: "
            "(1) exactly what needs to be done, "
            "(2) the definition of done — what completion looks like, "
            "(3) any key constraints, tools, or approach notes. "
            "No bullet points, no markdown. "
            "Be specific — this will be read by the person doing the work."
        ),
    },
}


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
            "After completing an action, give a specific confirmation: name the item and state the outcome clearly "
            "(e.g. 'Created task \"Fix login bug\" in project Backend, due Friday.'). "
            "If a tool returns an error, report what failed and suggest what the user can do next.\n\n"
            "TEAM ROLES AND PERMISSIONS:\n"
            "Every workspace has members with one of three roles. You must read the user's role from the USER CONTEXT "
            "and enforce these rules strictly — never carry out a restricted action even if the user asks.\n\n"
            "  owner — full control:\n"
            "    ✓ Everything admin can do\n"
            "    ✓ Delete the workspace\n"
            "    ✓ Transfer ownership to another member\n\n"
            "  admin — management access:\n"
            "    ✓ Invite new members and revoke invitations\n"
            "    ✓ Remove members from the workspace\n"
            "    ✓ Change member roles (cannot promote to owner)\n"
            "    ✓ Create, update, archive, and delete projects\n"
            "    ✓ Create, update, and delete any task in any project\n"
            "    ✓ Update workspace settings (name, description)\n"
            "    ✓ Create and manage plans\n\n"
            "  member — contributor access:\n"
            "    ✓ View all projects and tasks in their workspace\n"
            "    ✓ Create tasks in projects they belong to\n"
            "    ✓ Update tasks assigned to them or created by them\n"
            "    ✓ Upload and query documents\n"
            "    ✗ Cannot invite or remove members\n"
            "    ✗ Cannot change anyone's role\n"
            "    ✗ Cannot create, archive, or delete projects\n"
            "    ✗ Cannot delete tasks they did not create\n"
            "    ✗ Cannot change workspace settings\n"
            "    ✗ Cannot delete the workspace\n\n"
            "When a member asks you to do something they are not permitted to do:\n"
            "- Decline clearly and explain what role is needed.\n"
            "- Tell them to ask an admin or owner to do it.\n"
            "- Do NOT attempt the action, even partially.\n"
            "Example: 'Only admins and owners can invite members. Ask a workspace admin to send the invite.'\n\n"
            "RESPONSE STYLE:\n"
            "- Be direct and concise. Skip filler phrases like 'Of course!' or 'Sure thing!'.\n"
            "- Lead with results: state what was done before any explanation.\n"
            "- Use short bullet lists when presenting multiple items.\n"
            "- For questions or analysis, answer first — add supporting detail only if it adds value.\n\n"
            "WHAT NEVER TO SHOW THE USER:\n"
            "- Never reveal any numeric IDs — no workspace IDs, project IDs, task IDs, plan IDs, step IDs, user IDs, or any other internal database identifiers.\n"
            "- Never show raw JSON, tool call output, API responses, or any internal data structures.\n"
            "- Never mention field names like 'id', 'workspace_id', 'assigned_to_id', 'user_id', etc.\n"
            "- Refer to items by their name or title only. If you must distinguish two items with the same name, use context (e.g. the project under 'X workspace') not IDs.\n\n"
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
                "tool_calls": tool_calls_payload,  # type: ignore[typeddict-unknown-key]
            }
            history.append(assistant_msg)

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
                result = await dispatch(tc.function.name, args, db)
                try:
                    parsed_result = json.loads(result)
                    if "error" in parsed_result:
                        logger.warning(
                            "Tool %s returned error: %s",
                            tc.function.name,
                            parsed_result["error"],
                        )
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

    # ── Planner ───────────────────────────────────────────────────────────────

    async def decompose(self, goal: str) -> list[dict]:
        """Break a goal into an ordered list of plan step dicts."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": _PLANNER_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Goal: {goal}"},
                ],
                temperature=0.3,
                max_tokens=1024,
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
            return steps[:8]
        except Exception as exc:
            logger.warning("Plan decomposition failed: %s", exc)
            return [
                {
                    "title": goal,
                    "description": None,
                    "priority": "medium",
                    "depends_on": [],
                }
            ]

    # ── Form field suggestions ────────────────────────────────────────────────

    async def suggest_field(self, context_type: str, title: str, field: str) -> str:
        """Return a short AI-generated suggestion for a form field."""
        system = _SUGGEST_PROMPTS.get(context_type, {}).get(field)
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
