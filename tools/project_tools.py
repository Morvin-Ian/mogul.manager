import json
from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession

import models
from schemas.project.projects import ProjectCreate, ProjectRead, ProjectUpdate
from services.project.projects import ProjectService

PROJECT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_project",
            "description": "Create a new project inside a workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": [
                            "planning",
                            "active",
                            "on_hold",
                            "completed",
                            "archived",
                        ],
                    },
                    "due_date": {"type": "string", "description": "ISO 8601 date-time"},
                },
                "required": ["workspace_id", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_project",
            "description": "Update an existing project's title, description, status, or due date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": [
                            "planning",
                            "active",
                            "on_hold",
                            "completed",
                            "archived",
                        ],
                    },
                    "due_date": {
                        "type": "string",
                        "description": "ISO 8601 date-time, e.g. 2026-08-15T00:00:00Z",
                    },
                },
                "required": ["project_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_projects",
            "description": "List all projects inside a workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "integer"},
                    "limit": {
                        "type": "integer",
                        "description": "Max results (default 100)",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Skip N results (default 0)",
                    },
                },
                "required": ["workspace_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_project",
            "description": "Get full details of a specific project by ID.",
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
            "name": "delete_project",
            "description": "Permanently delete a project and all its tasks by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "integer"},
                },
                "required": ["project_id"],
            },
        },
    },
]


def _serialize(project: models.Project) -> dict:
    return ProjectRead.model_validate(project).model_dump(mode="json")


async def handle(name: str, args: dict, db: AsyncSession) -> str:
    svc = ProjectService(cast(AsyncSession, db))

    if name == "create_project":
        inp = ProjectCreate(**args)
        project = await svc.create(inp.model_dump(exclude_none=True))
        return json.dumps({"success": True, "project": _serialize(project)})

    if name == "update_project":
        project_id: int = args.pop("project_id")
        project = await svc.get_by_id(project_id)
        if not project:
            return json.dumps({"error": f"Project {project_id} not found"})
        inp = ProjectUpdate(**args)
        project = await svc.update(project, inp.model_dump(exclude_unset=True))
        return json.dumps({"success": True, "project": _serialize(project)})

    if name == "list_projects":
        projects = await svc.list_by_workspace(
            args["workspace_id"],
            skip=args.get("offset", 0),
            limit=args.get("limit", 100),
        )
        return json.dumps({"projects": [_serialize(p) for p in projects]})

    if name == "get_project":
        project = await svc.get_by_id(args["project_id"])
        if not project:
            return json.dumps({"error": f"Project {args['project_id']} not found"})
        return json.dumps({"project": _serialize(project)})

    if name == "delete_project":
        project = await svc.get_by_id(args["project_id"])
        if not project:
            return json.dumps({"error": f"Project {args['project_id']} not found"})
        await svc.delete(project)
        return json.dumps({"success": True, "deleted_project_id": args["project_id"]})

    return json.dumps({"error": f"Unknown project tool: {name}"})
