from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db


class CommentService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def create(self, comment_data: dict) -> models.Comment:
        comment = models.Comment(**comment_data)
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def get_by_id(self, comment_id: int) -> models.Comment | None:
        result = await self.db.execute(
            select(models.Comment).where(models.Comment.id == comment_id)
        )
        return result.scalars().first()

    async def list_by_task(
        self, task_id: int, skip: int = 0, limit: int = 100
    ) -> list[models.Comment]:
        result = await self.db.execute(
            select(models.Comment)
            .where(models.Comment.task_id == task_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(
        self, comment: models.Comment, update_data: dict
    ) -> models.Comment:
        for key, value in update_data.items():
            if value is not None:
                setattr(comment, key, value)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def delete(self, comment: models.Comment) -> None:
        await self.db.delete(comment)
        await self.db.commit()
