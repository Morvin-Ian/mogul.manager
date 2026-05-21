import json

from sqlalchemy.ext.asyncio import AsyncSession

from tools.project_tools import PROJECT_TOOLS
from tools.project_tools import handle as _handle_project
from tools.search_tools import SEARCH_TOOLS
from tools.search_tools import handle as _handle_search
from tools.task_tools import TASK_TOOLS
from tools.task_tools import handle as _handle_task

ALL_TOOLS = [*TASK_TOOLS, *PROJECT_TOOLS, *SEARCH_TOOLS]

_TASK_NAMES = {t["function"]["name"] for t in TASK_TOOLS}
_PROJECT_NAMES = {t["function"]["name"] for t in PROJECT_TOOLS}
_SEARCH_NAMES = {t["function"]["name"] for t in SEARCH_TOOLS}


async def dispatch(name: str, args: dict, db: AsyncSession) -> str:
    if name in _TASK_NAMES:
        return await _handle_task(name, args, db)
    if name in _PROJECT_NAMES:
        return await _handle_project(name, args, db)
    if name in _SEARCH_NAMES:
        return await _handle_search(name, args, db)
    return json.dumps({"error": f"Unknown tool: {name}"})
