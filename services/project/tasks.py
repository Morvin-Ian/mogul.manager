from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

import models
import uuid as _uuid_mod


def _is_valid_uuid(v: str) -> bool:
    try:
        _uuid_mod.UUID(v)
        return True
    except ValueError:
        return False


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

    async def list_by_workspace(
        self, workspace_id: int, status: str | None = None, skip: int = 0, limit: int = 200
    ) -> list[models.Task]:
        q = (
            select(models.Task)
            .join(models.Project, models.Task.project_id == models.Project.id)
            .options(
                joinedload(models.Task.assignee),
                selectinload(models.Task.project).selectinload(models.Project.workspace),
            )
            .where(models.Project.workspace_id == workspace_id)
        )
        if status:
            q = q.where(models.Task.status == status)
        result = await self.db.execute(q.offset(skip).limit(limit))
        return list(result.unique().scalars().all())

    async def list_by_project(
        self, project_id: int, skip: int = 0, limit: int = 100
    ) -> list[models.Task]:
        result = await self.db.execute(
            select(models.Task)
            .options(
                joinedload(models.Task.assignee),
                selectinload(models.Task.project).selectinload(models.Project.workspace),
            )
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

    async def get_by_uuid(self, uuid: str) -> models.Task | None:
        if not _is_valid_uuid(uuid):
            return None
        result = await self.db.execute(
            select(models.Task)
            .options(
                joinedload(models.Task.assignee),
                selectinload(models.Task.project).selectinload(models.Project.workspace),
            )
            .where(models.Task.uuid == uuid)
        )
        return result.unique().scalars().first()
