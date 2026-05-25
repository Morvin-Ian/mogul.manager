import json

from sqlalchemy.ext.asyncio import AsyncSession

from tools.document_tools import DOCUMENT_TOOLS
from tools.document_tools import handle as _handle_document
from tools.memory_tools import MEMORY_TOOLS
from tools.memory_tools import handle as _handle_memory
from tools.plan_tools import PLAN_TOOLS
from tools.plan_tools import handle as _handle_plan
from tools.project_tools import PROJECT_TOOLS
from tools.project_tools import handle as _handle_project
from tools.search_tools import SEARCH_TOOLS
from tools.search_tools import handle as _handle_search
from tools.task_tools import TASK_TOOLS
from tools.task_tools import handle as _handle_task
from tools.workspace_tools import WORKSPACE_TOOLS
from tools.workspace_tools import handle as _handle_workspace

ALL_TOOLS = [
    *DOCUMENT_TOOLS,
    *PLAN_TOOLS,
    *MEMORY_TOOLS,
    *WORKSPACE_TOOLS,
    *PROJECT_TOOLS,
    *TASK_TOOLS,
    *SEARCH_TOOLS,
]

_DOCUMENT_NAMES = {t["function"]["name"] for t in DOCUMENT_TOOLS}
_PLAN_NAMES = {t["function"]["name"] for t in PLAN_TOOLS}
_MEMORY_NAMES = {t["function"]["name"] for t in MEMORY_TOOLS}
_WORKSPACE_NAMES = {t["function"]["name"] for t in WORKSPACE_TOOLS}
_TASK_NAMES = {t["function"]["name"] for t in TASK_TOOLS}
_PROJECT_NAMES = {t["function"]["name"] for t in PROJECT_TOOLS}
_SEARCH_NAMES = {t["function"]["name"] for t in SEARCH_TOOLS}


async def dispatch(name: str, args: dict, db: AsyncSession) -> str:
    if name in _DOCUMENT_NAMES:
        return await _handle_document(name, args, db)
    if name in _PLAN_NAMES:
        return await _handle_plan(name, args, db)
    if name in _MEMORY_NAMES:
        return await _handle_memory(name, args, db)
    if name in _WORKSPACE_NAMES:
        return await _handle_workspace(name, args, db)
    if name in _TASK_NAMES:
        return await _handle_task(name, args, db)
    if name in _PROJECT_NAMES:
        return await _handle_project(name, args, db)
    if name in _SEARCH_NAMES:
        return await _handle_search(name, args, db)
    return json.dumps({"error": f"Unknown tool: {name}"})
