from fastapi import APIRouter, HTTPException, status

from schemas.memory import MemoryRead
from services.auth import CurrentUser
from services.memory import MemoryService
from typing import Annotated
from fastapi import Depends

router = APIRouter(prefix="/api/memory", tags=["Memory"])


@router.get("", response_model=list[MemoryRead])
async def list_memories(
    current_user: CurrentUser,
    service: Annotated[MemoryService, Depends()],
):
    return await service.list_by_user(current_user.id)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: int,
    current_user: CurrentUser,
    service: Annotated[MemoryService, Depends()],
):
    memory = await service.get_by_id(memory_id)
    if not memory or memory.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Memory not found")
    await service.delete(memory)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_all_memories(
    current_user: CurrentUser,
    service: Annotated[MemoryService, Depends()],
):
    await service.delete_all_for_user(current_user.id)
