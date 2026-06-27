import json
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

import models
from models.projects import (
    Project as _Project,  # noqa: F401 — used in _load_task_full selectinload
)
from schemas.project.tasks import TaskCreate, TaskRead, TaskUpdate
from services.project.tasks import TaskService


async def _load_task_full(task_id: int, db: AsyncSession) -> models.Task | None:
    """Fetch a task with project+workspace loaded so project_uuid serializes safely."""
    result = await db.execute(
        select(models.Task)
        .options(
            joinedload(models.Task.assignee),
            selectinload(models.Task.project).selectinload(models.Project.workspace),
        )
        .where(models.Task.id == task_id)
    )
    return result.unique().scalars().first()


TASK_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task inside a project. Use assigned_to_email to assign it to a team member.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "integer",
                        "description": "ID of the project",
                    },
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                    },
                    "status": {
                        "type": "string",
                        "enum": [
                            "todo",
                            "in_progress",
                            "review",
                            "blocked",
                            "completed",
                        ],
                    },
                    "assigned_to_email": {
                        "type": "string",
                        "description": "Email address of the team member to assign this task to. Use the email shown in the USER CONTEXT team list.",
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
            "description": "Update an existing task's fields, including reassigning it to a different team member.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": [
                            "todo",
                            "in_progress",
                            "review",
                            "blocked",
                            "completed",
                        ],
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                    },
                    "assigned_to_email": {
                        "type": "string",
                        "description": "Email of the team member to assign this task to. Use the email shown in the USER CONTEXT team list.",
                    },
                    "due_date": {"type": "string", "description": "ISO 8601 date-time"},
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
            "name": "assign_task",
            "description": "Assign or reassign a task to a specific team member by their email address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "ID of the task to assign",
                    },
                    "assigned_to_email": {
                        "type": "string",
                        "description": "Email address of the team member. Use the email shown in the USER CONTEXT team list.",
                    },
                },
                "required": ["task_id", "assigned_to_email"],
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
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 50)",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Skip N results (default 0)",
                    },
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


async def _resolve_assignee_email(
    args: dict, db: AsyncSession
) -> tuple[dict | None, str | None]:
    """Translate ``assigned_to_email`` into ``assigned_to_id`` and drop the email key.

    ``assigned_to_email`` is a schema-only convenience field — it is NOT a column on
    the Task model, so it must never reach ``TaskService``. Mirrors the HTTP route's
    ``_resolve_assignee_email`` but returns a JSON error string instead of raising,
    since tools surface errors as JSON to the agent.
    """
    args = {**args}
    email = args.pop("assigned_to_email", None)
    if not email:
        return args, None
    result = await db.execute(select(models.User).where(models.User.email == email))
    user = result.scalars().first()
    if not user:
        return None, json.dumps(
            {
                "error": f"No user found with email '{email}'. They must be a registered member of the workspace."
            }
        )
    args["assigned_to_id"] = user.id
    return args, None


async def handle(name: str, args: dict, db: AsyncSession) -> str:
    svc = TaskService(cast(AsyncSession, db))

    if name == "create_task":
        args, err = await _resolve_assignee_email(args, db)
        if err:
            return err
        inp = TaskCreate(**_coerce_priority(args))
        data = inp.model_dump(exclude_none=True)
        data.pop("assigned_to_email", None)
        task = await svc.create(data)
        task = await _load_task_full(task.id, db) or task
        return json.dumps({"success": True, "task": _serialize(task)})

    if name == "update_task":
        task_id: int = args.pop("task_id")
        task = await svc.get_by_id(task_id)
        if not task:
            return json.dumps({"error": f"Task {task_id} not found"})
        args, err = await _resolve_assignee_email(args, db)
        if err:
            return err
        inp = TaskUpdate(**_coerce_priority(args))
        data = inp.model_dump(exclude_unset=True)
        data.pop("assigned_to_email", None)
        task = await svc.update(task, data)
        task = await _load_task_full(task.id, db) or task
        return json.dumps({"success": True, "task": _serialize(task)})

    if name == "list_tasks":
        tasks = await svc.list_by_project(
            args["project_id"],
            skip=args.get("offset", 0),
            limit=args.get("limit", 50),
        )
        return json.dumps({"tasks": [_serialize(t) for t in tasks]})

    if name == "get_task":
        task = await _load_task_full(args["task_id"], db)
        if not task:
            return json.dumps({"error": f"Task {args['task_id']} not found"})
        return json.dumps({"task": _serialize(task)})

    if name == "assign_task":
        task_id: int = args["task_id"]
        task = await svc.get_by_id(task_id)
        if not task:
            return json.dumps({"error": f"Task {task_id} not found"})
        email = args["assigned_to_email"]
        user_result = await db.execute(
            select(models.User).where(models.User.email == email)
        )
        user = user_result.scalars().first()
        if not user:
            return json.dumps(
                {
                    "error": f"No user found with email '{email}'. They must be a registered member of the workspace."
                }
            )
        task = await svc.update(task, {"assigned_to_id": user.id})
        task = await _load_task_full(task.id, db) or task
        return json.dumps({"success": True, "task": _serialize(task)})

    if name == "delete_task":
        task = await svc.get_by_id(args["task_id"])
        if not task:
            return json.dumps({"error": f"Task {args['task_id']} not found"})
        await svc.delete(task)
        return json.dumps({"success": True, "deleted_task_id": args["task_id"]})

    return json.dumps({"error": f"Unknown task tool: {name}"})
