from typing import Annotated

from fastapi import Depends
from sqlalchemy import and_, or_, select
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
            .order_by(models.Comment.created_at)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_relevant(self, user_id: int, limit: int = 50) -> list[models.Comment]:
        """Recent comments that concern the user: on tasks assigned to them,
        on threads they participated in, or written by them.
        Excludes comments on completed tasks so the dashboard stays focused."""
        participated_task_ids = select(models.Comment.task_id).where(
            models.Comment.user_id == user_id
        )
        result = await self.db.execute(
            select(models.Comment)
            .join(models.Task, models.Task.id == models.Comment.task_id)
            .where(
                and_(
                    models.Task.status != models.TaskStatus.COMPLETED,
                    or_(
                        models.Comment.user_id == user_id,
                        models.Task.assigned_to_id == user_id,
                        models.Comment.task_id.in_(participated_task_ids),
                    ),
                )
            )
            .order_by(models.Comment.created_at.desc())
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
