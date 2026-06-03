from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from models.collaboration import WorkspaceMember
from database import get_db
from utils.uuid import is_valid_uuid as _is_valid_uuid


class ProjectService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def create(self, project_data: dict) -> models.Project:
        project = models.Project(**project_data)
        self.db.add(project)
        await self.db.commit()
        # Reload with workspace so workspace_uuid/workspace_title are available
        result = await self.db.execute(
            select(models.Project)
            .options(selectinload(models.Project.workspace))
            .where(models.Project.id == project.id)
        )
        return result.scalars().first() or project

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
        result = await self.db.execute(
            select(models.Project)
            .options(selectinload(models.Project.workspace))
            .where(models.Project.id == project.id)
        )
        return result.scalars().first() or project

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

    async def list_all_accessible(
        self, user_id: int, skip: int = 0, limit: int = 500
    ) -> list[models.Project]:
        accessible_ws_ids = select(WorkspaceMember.workspace_id).where(
            WorkspaceMember.user_id == user_id
        )
        result = await self.db.execute(
            select(models.Project)
            .options(selectinload(models.Project.workspace))
            .where(models.Project.workspace_id.in_(accessible_ws_ids))
            .order_by(models.Project.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
