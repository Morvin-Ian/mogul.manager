from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import models
from database import get_db


class ActivityService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def log(
        self,
        user_id: int,
        entity_type: str,
        entity_id: int,
        action: str,
        workspace_id: int | None = None,
        project_id: int | None = None,
        task_id: int | None = None,
        summary: str | None = None,
        changes: dict | None = None,
    ) -> models.ActivityLog:
        entry = models.ActivityLog(
            workspace_id=workspace_id,
            project_id=project_id,
            task_id=task_id,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            summary=summary,
            changes=changes,
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def list_by_workspace(
        self, workspace_id: int, skip: int = 0, limit: int = 50
    ) -> list[models.ActivityLog]:
        result = await self.db.execute(
            select(models.ActivityLog)
            .options(joinedload(models.ActivityLog.user))
            .where(models.ActivityLog.workspace_id == workspace_id)
            .order_by(models.ActivityLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.unique().scalars().all())

    async def list_by_project(
        self, project_id: int, skip: int = 0, limit: int = 50
    ) -> list[models.ActivityLog]:
        result = await self.db.execute(
            select(models.ActivityLog)
            .options(joinedload(models.ActivityLog.user))
            .where(models.ActivityLog.project_id == project_id)
            .order_by(models.ActivityLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.unique().scalars().all())

    async def list_by_task(
        self, task_id: int, skip: int = 0, limit: int = 50
    ) -> list[models.ActivityLog]:
        result = await self.db.execute(
            select(models.ActivityLog)
            .options(joinedload(models.ActivityLog.user))
            .where(models.ActivityLog.task_id == task_id)
            .order_by(models.ActivityLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.unique().scalars().all())
