import json

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models

SEARCH_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_tasks",
            "description": "Search tasks by a keyword in their title. Optionally filter by project or status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Keyword to match in task titles"},
                    "project_id": {
                        "type": "integer",
                        "description": "Limit search to this project (optional)",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["todo", "in_progress", "review", "blocked", "completed"],
                        "description": "Filter by status (optional)",
                    },
                },
                "required": ["query"],
            },
        },
    },
]

_STATUS_MAP = {
    "todo": models.TaskStatus.TODO,
    "in_progress": models.TaskStatus.IN_PROGRESS,
    "review": models.TaskStatus.REVIEW,
    "blocked": models.TaskStatus.BLOCKED,
    "completed": models.TaskStatus.COMPLETED,
}


class SearchTasksInput(BaseModel):
    query: str
    project_id: int | None = None
    status: str | None = None


async def handle(name: str, args: dict, db: AsyncSession) -> str:
    if name == "search_tasks":
        inp = SearchTasksInput(**args)
        pattern = f"%{inp.query}%"
        stmt = select(models.Task).where(
            models.Task.title.ilike(pattern) | models.Task.description.ilike(pattern)
        )
        if inp.project_id is not None:
            stmt = stmt.where(models.Task.project_id == inp.project_id)
        if inp.status is not None:
            stmt = stmt.where(models.Task.status == _STATUS_MAP[inp.status])
        result = await db.execute(stmt.limit(20))
        tasks = list(result.scalars().all())
        return json.dumps({
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status.value,
                    "priority": t.priority.value,
                    "project_id": t.project_id,
                }
                for t in tasks
            ]
        })

    return json.dumps({"error": f"Unknown search tool: {name}"})
