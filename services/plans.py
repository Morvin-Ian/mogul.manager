from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db


class PlanService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def create(self, user_id: int, data: dict) -> models.Plan:
        plan = models.Plan(user_id=user_id, **data)
        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)
        return plan

    async def get_by_id(self, plan_id: int) -> models.Plan | None:
        result = await self.db.execute(
            select(models.Plan).where(models.Plan.id == plan_id)
        )
        return result.scalars().first()

    async def get_detail(self, plan_id: int) -> models.Plan | None:
        result = await self.db.execute(
            select(models.Plan)
            .options(selectinload(models.Plan.steps))
            .where(models.Plan.id == plan_id)
        )
        return result.scalars().first()

    async def list_by_user(self, user_id: int) -> list[models.Plan]:
        result = await self.db.execute(
            select(models.Plan)
            .options(selectinload(models.Plan.steps))
            .where(models.Plan.user_id == user_id)
            .order_by(models.Plan.updated_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, plan: models.Plan, data: dict) -> models.Plan:
        for key, value in data.items():
            setattr(plan, key, value)
        await self.db.commit()
        await self.db.refresh(plan)
        return plan

    async def delete(self, plan: models.Plan) -> None:
        await self.db.delete(plan)
        await self.db.commit()

    async def create_step(self, data: dict) -> models.PlanStep:
        step = models.PlanStep(**data)
        self.db.add(step)
        await self.db.commit()
        await self.db.refresh(step)
        return step

    async def get_step(self, step_id: int) -> models.PlanStep | None:
        result = await self.db.execute(
            select(models.PlanStep).where(models.PlanStep.id == step_id)
        )
        return result.scalars().first()

    async def update_step(self, step: models.PlanStep, data: dict) -> models.PlanStep:
        for key, value in data.items():
            if value is not None:
                setattr(step, key, value)
        await self.db.commit()
        await self.db.refresh(step)
        # Sync plan status after step update
        await self._sync_plan_status(step.plan_id)
        return step

    async def _sync_plan_status(self, plan_id: int) -> None:
        plan = await self.get_detail(plan_id)
        if not plan or not plan.steps:
            return
        statuses = {s.status for s in plan.steps}
        if all(s.status.value in ("completed", "skipped") for s in plan.steps):
            plan.status = models.PlanStatus.COMPLETED
        elif any(s.status == models.StepStatus.RUNNING for s in plan.steps):
            plan.status = models.PlanStatus.ACTIVE
        await self.db.commit()
