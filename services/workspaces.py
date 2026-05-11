from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db


class WorkspaceService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def create(self, workspace_data: dict, user_id: int) -> models.Workspace:
        workspace = models.Workspace(**workspace_data, user_id=user_id)
        self.db.add(workspace)
        await self.db.commit()
        await self.db.refresh(workspace)
        return workspace

    async def get_by_id(self, workspace_id: int) -> models.Workspace | None:
        result = await self.db.execute(
            select(models.Workspace).where(models.Workspace.id == workspace_id)
        )
        return result.scalars().first()

    async def list_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[models.Workspace]:
        result = await self.db.execute(
            select(models.Workspace)
            .where(models.Workspace.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(
        self, workspace: models.Workspace, update_data: dict
    ) -> models.Workspace:
        for key, value in update_data.items():
            if value is not None:
                setattr(workspace, key, value)
        await self.db.commit()
        await self.db.refresh(workspace)
        return workspace

    async def delete(self, workspace: models.Workspace) -> None:
        await self.db.delete(workspace)
        await self.db.commit()
