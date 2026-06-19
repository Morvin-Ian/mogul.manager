import asyncio
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from tools.document_tools import DOCUMENT_TOOLS
from tools.document_tools import handle as _handle_document
from tools.memory_tools import MEMORY_TOOLS
from tools.memory_tools import handle as _handle_memory
from tools.project_tools import PROJECT_TOOLS
from tools.project_tools import handle as _handle_project
from tools.search_tools import SEARCH_TOOLS
from tools.search_tools import handle as _handle_search
from tools.plan_tools import PLAN_TOOLS
from tools.plan_tools import handle as _handle_plan
from tools.task_tools import TASK_TOOLS
from tools.task_tools import handle as _handle_task
from tools.workspace_tools import WORKSPACE_TOOLS
from tools.workspace_tools import handle as _handle_workspace

logger = logging.getLogger(__name__)

ALL_TOOLS = [
    *DOCUMENT_TOOLS,
    *MEMORY_TOOLS,
    *WORKSPACE_TOOLS,
    *PROJECT_TOOLS,
    *TASK_TOOLS,
    *PLAN_TOOLS,
    *SEARCH_TOOLS,
]

_DOCUMENT_NAMES = {t["function"]["name"] for t in DOCUMENT_TOOLS}
_MEMORY_NAMES = {t["function"]["name"] for t in MEMORY_TOOLS}
_WORKSPACE_NAMES = {t["function"]["name"] for t in WORKSPACE_TOOLS}
_TASK_NAMES = {t["function"]["name"] for t in TASK_TOOLS}
_PROJECT_NAMES = {t["function"]["name"] for t in PROJECT_TOOLS}
_SEARCH_NAMES = {t["function"]["name"] for t in SEARCH_TOOLS}
_PLAN_NAMES = {t["function"]["name"] for t in PLAN_TOOLS}

_MAX_RETRIES = 2
_RETRYABLE_ERROR_SUBSTRINGS = (
    "temporarily unavailable",
    "timeout",
    "connection",
    "503",
    "502",
    "503 Service Unavailable",
    "internal server error",
    "too many requests",
)


def _is_retryable(result: str) -> bool:
    lower = result.lower()
    return any(sub in lower for sub in _RETRYABLE_ERROR_SUBSTRINGS)


async def dispatch(name: str, args: dict, db: AsyncSession, user_id: int = 0) -> str:
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            if name in _DOCUMENT_NAMES:
                result = await _handle_document(name, args, db)
            elif name in _MEMORY_NAMES:
                result = await _handle_memory(name, args, db)
            elif name in _WORKSPACE_NAMES:
                result = await _handle_workspace(name, args, db)
            elif name in _TASK_NAMES:
                result = await _handle_task(name, args, db)
            elif name in _PROJECT_NAMES:
                result = await _handle_project(name, args, db)
            elif name in _SEARCH_NAMES:
                result = await _handle_search(name, args, db)
            elif name in _PLAN_NAMES:
                result = await _handle_plan(name, args, db, user_id)
            else:
                return json.dumps({"error": f"Unknown tool: {name}"})

            if attempt > 1 or (_is_retryable(result) and attempt < _MAX_RETRIES):
                logger.warning(
                    "Tool %s attempt %d: %s",
                    name, attempt, result[:200] if _is_retryable(result) else "OK",
                )

            if _is_retryable(result) and attempt < _MAX_RETRIES:
                wait = 0.5 * attempt
                await asyncio.sleep(wait)
                continue

            return result

        except Exception as exc:
            logger.warning("Tool %s attempt %d failed: %s", name, attempt, exc)
            if attempt < _MAX_RETRIES:
                await asyncio.sleep(0.5 * attempt)
                continue
            return json.dumps({"error": f"Tool {name} failed after {_MAX_RETRIES} attempts: {exc}"})

    return json.dumps({"error": f"Tool {name} failed after retries"})
