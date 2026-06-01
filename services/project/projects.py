from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

import models
import uuid as _uuid_mod


def _is_valid_uuid(v: str) -> bool:
    try:
        _uuid_mod.UUID(v)
        return True
    except ValueError:
        return False


from database import get_db


class ProjectService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def create(self, project_data: dict) -> models.Project:
        project = models.Project(**project_data)
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def get_by_id(self, project_id: int) -> models.Project | None:
        result = await self.db.execute(
            select(models.Project).where(models.Project.id == project_id)
        )
        return result.scalars().first()

    async def list_by_workspace(
        self, workspace_id: int, skip: int = 0, limit: int = 100
    ) -> list[models.Project]:
        result = await self.db.execute(
            select(models.Project)
            .options(selectinload(models.Project.workspace))
            .where(models.Project.workspace_id == workspace_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(
        self, project: models.Project, update_data: dict
    ) -> models.Project:
        for key, value in update_data.items():
            if value is not None:
                setattr(project, key, value)
        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def delete(self, project: models.Project) -> None:
        await self.db.delete(project)
        await self.db.commit()

    async def get_by_uuid(self, uuid: str) -> models.Project | None:
        if not _is_valid_uuid(uuid):
            return None
        result = await self.db.execute(
            select(models.Project)
            .options(selectinload(models.Project.workspace))
            .where(models.Project.uuid == uuid)
        )
        return result.scalars().first()
