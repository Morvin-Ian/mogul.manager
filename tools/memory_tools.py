import json

from sqlalchemy.ext.asyncio import AsyncSession

import models
from schemas.memory import MemoryRead
from services.memory import MemoryService

MEMORY_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "store_memory",
            "description": (
                "Save an important fact, preference, decision, or goal about the user "
                "to long-term memory so it can be recalled in future conversations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "The current user's ID"},
                    "memory_type": {
                        "type": "string",
                        "enum": ["preference", "decision", "goal", "fact"],
                    },
                    "content": {
                        "type": "string",
                        "description": "A single concise sentence describing what to remember",
                    },
                    "importance": {
                        "type": "integer",
                        "description": "1=useful, 2=important, 3=critical",
                        "enum": [1, 2, 3],
                    },
                },
                "required": ["user_id", "memory_type", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_memories",
            "description": "Retrieve all stored long-term memories about the current user.",
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
            "name": "delete_memory",
            "description": "Delete a specific memory that is outdated or incorrect.",
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_id": {"type": "integer"},
                },
                "required": ["memory_id"],
            },
        },
    },
]


def _serialize(memory: models.Memory) -> dict:
    return MemoryRead.model_validate(memory).model_dump(mode="json")


async def handle(name: str, args: dict, db: AsyncSession) -> str:
    svc = MemoryService(db)  # type: ignore[arg-type]

    if name == "store_memory":
        user_id: int = args.pop("user_id")
        memory = await svc.create(
            user_id=user_id,
            memory_data={
                "memory_type": args["memory_type"],
                "content": args["content"],
                "importance": args.get("importance", 1),
            },
        )
        return json.dumps({"success": True, "memory": _serialize(memory)})

    if name == "list_memories":
        memories = await svc.list_by_user(args["user_id"])
        return json.dumps({"memories": [_serialize(m) for m in memories]})

    if name == "delete_memory":
        memory = await svc.get_by_id(args["memory_id"])
        if not memory:
            return json.dumps({"error": f"Memory {args['memory_id']} not found"})
        await svc.delete(memory)
        return json.dumps({"success": True, "deleted_memory_id": args["memory_id"]})

    return json.dumps({"error": f"Unknown memory tool: {name}"})
