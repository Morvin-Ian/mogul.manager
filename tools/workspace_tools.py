import json

from sqlalchemy.ext.asyncio import AsyncSession

import models
from schemas.workspaces import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate
from services.workspaces import WorkspaceService

WORKSPACE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_workspace",
            "description": "Create a new workspace for the current user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "The current user's ID"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "settings": {"type": "object"},
                },
                "required": ["user_id", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_workspace",
            "description": "Update an existing workspace's title, description, settings, or archived state.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "settings": {"type": "object"},
                    "is_archived": {"type": "boolean"},
                },
                "required": ["workspace_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_workspaces",
            "description": "List all workspaces belonging to the current user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "The current user's ID"},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_workspace",
            "description": "Get full details of a specific workspace by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "integer"},
                },
                "required": ["workspace_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_workspace",
            "description": "Permanently delete a workspace and all its projects by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "integer"},
                },
                "required": ["workspace_id"],
            },
        },
    },
]


def _serialize(workspace: models.Workspace) -> dict:
    return WorkspaceRead.model_validate(workspace).model_dump(mode="json")


async def handle(name: str, args: dict, db: AsyncSession) -> str:
    svc = WorkspaceService(db)  # type: ignore[arg-type]

    if name == "create_workspace":
        user_id: int = args.pop("user_id")
        inp = WorkspaceCreate(**args)
        workspace = await svc.create(inp.model_dump(exclude_none=True), user_id)
        return json.dumps({"success": True, "workspace": _serialize(workspace)})

    if name == "update_workspace":
        workspace_id: int = args.pop("workspace_id")
        workspace = await svc.get_by_id(workspace_id)
        if not workspace:
            return json.dumps({"error": f"Workspace {workspace_id} not found"})
        inp = WorkspaceUpdate(**args)
        workspace = await svc.update(workspace, inp.model_dump(exclude_unset=True))
        return json.dumps({"success": True, "workspace": _serialize(workspace)})

    if name == "list_workspaces":
        workspaces = await svc.list_by_user(args["user_id"])
        return json.dumps({"workspaces": [_serialize(w) for w in workspaces]})

    if name == "get_workspace":
        workspace = await svc.get_by_id(args["workspace_id"])
        if not workspace:
            return json.dumps({"error": f"Workspace {args['workspace_id']} not found"})
        return json.dumps({"workspace": _serialize(workspace)})

    if name == "delete_workspace":
        workspace = await svc.get_by_id(args["workspace_id"])
        if not workspace:
            return json.dumps({"error": f"Workspace {args['workspace_id']} not found"})
        await svc.delete(workspace)
        return json.dumps({"success": True, "deleted_workspace_id": args["workspace_id"]})

    return json.dumps({"error": f"Unknown workspace tool: {name}"})
