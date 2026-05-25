import json

from sqlalchemy.ext.asyncio import AsyncSession

import models
from schemas.project.tasks import TaskCreate, TaskRead, TaskUpdate
from services.project.tasks import TaskService

TASK_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task inside a project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer", "description": "ID of the project"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                    },
                    "status": {
                        "type": "string",
                        "enum": ["todo", "in_progress", "review", "blocked", "completed"],
                    },
                    "estimated_hours": {"type": "integer"},
                    "due_date": {"type": "string", "description": "ISO 8601 date-time"},
                },
                "required": ["project_id", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task's fields.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["todo", "in_progress", "review", "blocked", "completed"],
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                    },
                    "estimated_hours": {"type": "integer"},
                    "actual_hours": {"type": "integer"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks in a project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer"},
                },
                "required": ["project_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_task",
            "description": "Get full details of a specific task by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Permanently delete a task by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                },
                "required": ["task_id"],
            },
        },
    },
]


_PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3, "urgent": 4}


def _coerce_priority(args: dict) -> dict:
    if "priority" in args and isinstance(args["priority"], str):
        args = {**args, "priority": _PRIORITY_MAP.get(args["priority"], 2)}
    return args


def _serialize(task: models.Task) -> dict:
    return TaskRead.model_validate(task).model_dump(mode="json")


async def handle(name: str, args: dict, db: AsyncSession) -> str:
    svc = TaskService(db)  # type: ignore[arg-type]

    if name == "create_task":
        inp = TaskCreate(**_coerce_priority(args))
        task = await svc.create(inp.model_dump(exclude_none=True))
        return json.dumps({"success": True, "task": _serialize(task)})

    if name == "update_task":
        task_id: int = args.pop("task_id")
        task = await svc.get_by_id(task_id)
        if not task:
            return json.dumps({"error": f"Task {task_id} not found"})
        inp = TaskUpdate(**_coerce_priority(args))
        task = await svc.update(task, inp.model_dump(exclude_unset=True))
        return json.dumps({"success": True, "task": _serialize(task)})

    if name == "list_tasks":
        tasks = await svc.list_by_project(args["project_id"])
        return json.dumps({"tasks": [_serialize(t) for t in tasks]})

    if name == "get_task":
        task = await svc.get_by_id(args["task_id"])
        if not task:
            return json.dumps({"error": f"Task {args['task_id']} not found"})
        return json.dumps({"task": _serialize(task)})

    if name == "delete_task":
        task = await svc.get_by_id(args["task_id"])
        if not task:
            return json.dumps({"error": f"Task {args['task_id']} not found"})
        await svc.delete(task)
        return json.dumps({"success": True, "deleted_task_id": args["task_id"]})

    return json.dumps({"error": f"Unknown task tool: {name}"})
