from typing import Annotated

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db


class TagService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def list_by_project(self, project_id: int) -> list[models.Tag]:
        result = await self.db.execute(
            select(models.Tag)
            .where(models.Tag.project_id == project_id)
            .order_by(models.Tag.name)
        )
        return list(result.scalars().all())

    async def create(self, project_id: int, name: str, color: str) -> models.Tag:
        tag = models.Tag(project_id=project_id, name=name, color=color)
        self.db.add(tag)
        await self.db.commit()
        await self.db.refresh(tag)
        return tag

    async def update(self, tag_id: int, name: str | None, color: str | None) -> models.Tag | None:
        result = await self.db.execute(select(models.Tag).where(models.Tag.id == tag_id))
        tag = result.scalars().first()
        if not tag:
            return None
        if name is not None:
            tag.name = name
        if color is not None:
            tag.color = color
        await self.db.commit()
        await self.db.refresh(tag)
        return tag

    async def delete(self, tag_id: int) -> bool:
        result = await self.db.execute(select(models.Tag).where(models.Tag.id == tag_id))
        tag = result.scalars().first()
        if not tag:
            return False
        await self.db.delete(tag)
        await self.db.commit()
        return True

    async def attach_to_task(self, task_id: int, tag_id: int) -> bool:
        result = await self.db.execute(select(models.Tag).where(models.Tag.id == tag_id))
        tag = result.scalars().first()
        if not tag:
            return False
        result = await self.db.execute(
            select(models.Task).where(models.Task.id == task_id).options(selectinload(models.Task.tags))
        )
        task = result.scalars().first()
        if not task:
            return False
        if tag not in task.tags:
            task.tags.append(tag)
            await self.db.commit()
        return True

    async def detach_from_task(self, task_id: int, tag_id: int) -> bool:
        result = await self.db.execute(
            select(models.Task).where(models.Task.id == task_id).options(selectinload(models.Task.tags))
        )
        task = result.scalars().first()
        if not task:
            return False
        tag = next((t for t in task.tags if t.id == tag_id), None)
        if not tag:
            return False
        task.tags.remove(tag)
        await self.db.commit()
        return True

    async def list_task_tags(self, task_id: int) -> list[models.Tag]:
        result = await self.db.execute(
            select(models.Task)
            .where(models.Task.id == task_id)
            .options(selectinload(models.Task.tags))
        )
        task = result.scalars().first()
        return list(task.tags) if task else []
