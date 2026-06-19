from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db


class MemoryService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def create(
        self, user_id: int, memory_data: dict, workspace_id: int | None = None
    ) -> models.Memory:
        memory = models.Memory(
            user_id=user_id, workspace_id=workspace_id, **memory_data
        )
        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)
        return memory

    async def get_by_id(self, memory_id: int) -> models.Memory | None:
        result = await self.db.execute(
            select(models.Memory).where(models.Memory.id == memory_id)
        )
        return result.scalars().first()

    async def list_by_user(self, user_id: int, limit: int = 20) -> list[models.Memory]:
        now = datetime.now(UTC)
        result = await self.db.execute(
            select(models.Memory)
            .where(models.Memory.user_id == user_id)
            .order_by(
                models.Memory.importance.desc(),
                models.Memory.last_accessed_at.desc().nulls_last(),
                models.Memory.updated_at.desc(),
            )
            .limit(limit)
        )
        memories = list(result.scalars().all())
        for mem in memories:
            if (
                mem.last_accessed_at is None
                or (now - mem.last_accessed_at.replace(tzinfo=UTC)).total_seconds()
                > 3600
            ):
                await self._touch(mem)
        return memories

    async def list_by_workspace(
        self, workspace_id: int, limit: int = 20
    ) -> list[models.Memory]:
        result = await self.db.execute(
            select(models.Memory)
            .where(models.Memory.workspace_id == workspace_id)
            .order_by(
                models.Memory.importance.desc(),
                models.Memory.updated_at.desc(),
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_combined(
        self, user_id: int, workspace_id: int | None = None, limit: int = 20
    ) -> list[models.Memory]:
        conditions = [models.Memory.user_id == user_id]
        if workspace_id is not None:
            conditions.append(models.Memory.workspace_id == workspace_id)
        else:
            conditions.append(models.Memory.workspace_id.is_(None))

        result = await self.db.execute(
            select(models.Memory)
            .where(or_(*conditions) if len(conditions) > 1 else conditions[0])
            .order_by(
                models.Memory.importance.desc(),
                models.Memory.updated_at.desc(),
            )
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

    async def _touch(self, memory: models.Memory) -> None:
        memory.last_accessed_at = datetime.now(UTC)
        await self.db.execute(
            update(models.Memory)
            .where(models.Memory.id == memory.id)
            .values(last_accessed_at=datetime.now(UTC))
        )
        await self.db.commit()

    async def get_stale_memories(
        self, user_id: int, max_importance: int = 1, limit: int = 50
    ) -> list[models.Memory]:
        result = await self.db.execute(
            select(models.Memory)
            .where(
                models.Memory.user_id == user_id,
                models.Memory.importance <= max_importance,
            )
            .order_by(models.Memory.updated_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def summarize_and_replace(
        self,
        user_id: int,
        memories: list[models.Memory],
        summary_content: str,
    ) -> models.Memory | None:
        if not memories:
            return None
        for mem in memories:
            await self.db.delete(mem)
        summary = models.Memory(
            user_id=user_id,
            memory_type="fact",
            content=summary_content,
            importance=1,
        )
        self.db.add(summary)
        await self.db.commit()
        await self.db.refresh(summary)
        return summary
