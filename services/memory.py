from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db


class MemoryService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def create(self, user_id: int, memory_data: dict) -> models.Memory:
        memory = models.Memory(user_id=user_id, **memory_data)
        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)
        return memory

    async def get_by_id(self, memory_id: int) -> models.Memory | None:
        result = await self.db.execute(
            select(models.Memory).where(models.Memory.id == memory_id)
        )
        return result.scalars().first()

    async def list_by_user(
        self, user_id: int, limit: int = 20
    ) -> list[models.Memory]:
        result = await self.db.execute(
            select(models.Memory)
            .where(models.Memory.user_id == user_id)
            .order_by(models.Memory.importance.desc(), models.Memory.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete(self, memory: models.Memory) -> None:
        await self.db.delete(memory)
        await self.db.commit()

    async def delete_all_for_user(self, user_id: int) -> int:
        memories = await self.list_by_user(user_id, limit=1000)
        for m in memories:
            await self.db.delete(m)
        await self.db.commit()
        return len(memories)
