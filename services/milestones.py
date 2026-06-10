from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db


class MilestoneService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def list_by_project(self, project_id: int) -> list[models.Milestone]:
        result = await self.db.execute(
            select(models.Milestone)
            .where(models.Milestone.project_id == project_id)
            .order_by(models.Milestone.due_date.asc().nulls_last(), models.Milestone.created_at.asc())
        )
        return list(result.scalars().all())

    async def create(
        self, project_id: int, name: str, description: str | None = None, due_date: datetime | None = None
    ) -> models.Milestone:
        m = models.Milestone(
            project_id=project_id,
            name=name,
            description=description,
            due_date=due_date,
        )
        self.db.add(m)
        await self.db.commit()
        await self.db.refresh(m)
        return m

    async def update(
        self,
        milestone_id: int,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
        due_date: datetime | None = None,
    ) -> models.Milestone | None:
        result = await self.db.execute(
            select(models.Milestone).where(models.Milestone.id == milestone_id)
        )
        m = result.scalars().first()
        if not m:
            return None
        if name is not None:
            m.name = name
        if description is not None:
            m.description = description
        if status is not None:
            m.status = models.MilestoneStatus(status)
            if status == "achieved" and not m.achieved_at:
                m.achieved_at = datetime.now(UTC)
            elif status != "achieved":
                m.achieved_at = None
        if due_date is not None:
            m.due_date = due_date
        await self.db.commit()
        await self.db.refresh(m)
        return m

    async def delete(self, milestone_id: int) -> bool:
        result = await self.db.execute(
            select(models.Milestone).where(models.Milestone.id == milestone_id)
        )
        m = result.scalars().first()
        if not m:
            return False
        await self.db.delete(m)
        await self.db.commit()
        return True
