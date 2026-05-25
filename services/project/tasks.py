from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import models
from database import get_db


class TaskService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def create(self, task_data: dict) -> models.Task:
        task = models.Task(**task_data)
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return await self._load_assignee(task)

    async def get_by_id(self, task_id: int) -> models.Task | None:
        result = await self.db.execute(
            select(models.Task)
            .options(joinedload(models.Task.assignee))
            .where(models.Task.id == task_id)
        )
        return result.unique().scalars().first()

    async def list_by_project(
        self, project_id: int, skip: int = 0, limit: int = 100
    ) -> list[models.Task]:
        result = await self.db.execute(
            select(models.Task)
            .options(joinedload(models.Task.assignee))
            .where(models.Task.project_id == project_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.unique().scalars().all())

    async def update(self, task: models.Task, update_data: dict) -> models.Task:
        for key, value in update_data.items():
            if value is not None:
                setattr(task, key, value)
        await self.db.commit()
        await self.db.refresh(task)
        return await self._load_assignee(task)

    async def delete(self, task: models.Task) -> None:
        await self.db.delete(task)
        await self.db.commit()

    async def _load_assignee(self, task: models.Task) -> models.Task:
        result = await self.db.execute(
            select(models.Task)
            .options(joinedload(models.Task.assignee))
            .where(models.Task.id == task.id)
        )
        loaded = result.unique().scalars().first()
        return loaded or task
