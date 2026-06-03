import re
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

import models
from database import get_db
from models.plans import PlanStatus, StepPriority, StepStatus
from utils.uuid import is_valid_uuid as _is_valid_uuid

# Strip patterns like "id=42", "id: 42", "task id 5", "task_id=5" from AI text
_ID_PATTERN = re.compile(
    r'\b(?:task[_\s-]?id|step[_\s-]?id|id)\s*[=:]\s*\d+\b',
    re.IGNORECASE,
)

class PlanService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    # ── Queries ───────────────────────────────────────────────────────────────

    async def get_by_uuid(self, uuid: str) -> models.Plan | None:
        if not _is_valid_uuid(uuid):
            return None
        result = await self.db.execute(
            select(models.Plan)
            .options(
                joinedload(models.Plan.project),
                selectinload(models.Plan.steps).joinedload(models.PlanStep.linked_task),
            )
            .where(models.Plan.uuid == uuid)
        )
        return result.unique().scalars().first()

    async def get_step_by_uuid(self, uuid: str) -> models.PlanStep | None:
        if not _is_valid_uuid(uuid):
            return None
        result = await self.db.execute(
            select(models.PlanStep)
            .options(joinedload(models.PlanStep.linked_task))
            .where(models.PlanStep.uuid == uuid)
        )
        return result.unique().scalars().first()

    async def list_by_project(self, project_id: int) -> list[models.Plan]:
        result = await self.db.execute(
            select(models.Plan)
            .options(
                joinedload(models.Plan.project),
                selectinload(models.Plan.steps).joinedload(models.PlanStep.linked_task),
            )
            .where(models.Plan.project_id == project_id)
            .order_by(models.Plan.created_at.desc())
        )
        return list(result.unique().scalars().all())

    # ── Creation (AI-driven) ──────────────────────────────────────────────────

    async def create(
        self,
        project_id: int,
        user_id: int,
        title: str,
        description: str | None,
    ) -> models.Plan:
        project = await self._load_project(project_id)

        # Fetch existing tasks so the AI can link instead of duplicate
        existing_tasks = await self._fetch_task_context(project_id)

        goal_parts = [f"Project: {project.title}"]
        if project.description:
            goal_parts.append(f"Description: {project.description}")
        goal_parts.append(f"Plan goal: {title}")
        if description:
            goal_parts.append(f"Additional context: {description}")
        goal = "\n".join(goal_parts)

        from agents.deepseek import DeepSeekAgent  # local import avoids circular dependency
        raw_steps = await DeepSeekAgent().decompose(
            goal=goal,
            existing_tasks=existing_tasks,
        )

        plan = models.Plan(
            project_id=project_id,
            user_id=user_id,
            title=title,
            description=description,
            status=PlanStatus.ACTIVE,
        )
        self.db.add(plan)
        await self.db.flush()  # get plan.id before creating steps

        for order, raw in enumerate(raw_steps):
            task_spec = raw.get("task") or {}
            linked_task_id = await self._resolve_task(task_spec, project_id, user_id)

            priority_val = raw.get("priority", "medium")
            try:
                priority = StepPriority(priority_val)
            except ValueError:
                priority = StepPriority.MEDIUM

            raw_title = raw.get("title", f"Step {order + 1}")
            raw_desc = raw.get("description")
            clean_title = _ID_PATTERN.sub("", raw_title).strip()
            clean_desc = _ID_PATTERN.sub("", raw_desc).strip() if raw_desc else None

            step = models.PlanStep(
                plan_id=plan.id,
                title=clean_title or raw_title,
                description=clean_desc or None,
                step_order=order,
                priority=priority,
                status=StepStatus.PENDING,
                dependencies=raw.get("depends_on") or [],
                linked_task_id=linked_task_id,
                agent_notes=None,
            )
            self.db.add(step)

        await self.db.commit()
        return await self._reload(plan.id)

    # ── Plan CRUD ─────────────────────────────────────────────────────────────

    async def update(self, plan: models.Plan, data: dict) -> models.Plan:
        for key, value in data.items():
            setattr(plan, key, value)
        await self.db.commit()
        return await self._reload(plan.id)

    async def delete(self, plan: models.Plan) -> None:
        # Unlink tasks created by this plan's steps (do NOT delete them)
        for step in plan.steps:
            step.linked_task_id = None
        await self.db.delete(plan)
        await self.db.commit()

    # ── Step CRUD ─────────────────────────────────────────────────────────────

    async def add_step(
        self,
        plan: models.Plan,
        title: str,
        description: str | None,
        priority: StepPriority,
        step_order: int | None,
    ) -> models.Plan:
        order = step_order if step_order is not None else len(plan.steps)
        step = models.PlanStep(
            plan_id=plan.id,
            title=title,
            description=description,
            step_order=order,
            priority=priority,
            status=StepStatus.PENDING,
            dependencies=[],
        )
        self.db.add(step)
        await self.db.commit()
        return await self._reload(plan.id)

    async def update_step(self, step: models.PlanStep, data: dict) -> models.PlanStep:
        for key, value in data.items():
            setattr(step, key, value)
        await self.db.commit()

        # Sync linked task status when step status changes
        if "status" in data and step.linked_task_id:
            await self._sync_task_from_step(step)

        await self._sync_plan_status(step.plan_id)
        result = await self.db.execute(
            select(models.PlanStep)
            .options(joinedload(models.PlanStep.linked_task))
            .where(models.PlanStep.id == step.id)
        )
        return result.unique().scalars().first() or step

    async def delete_step(self, step: models.PlanStep) -> None:
        plan_id = step.plan_id
        await self.db.delete(step)
        await self.db.commit()
        await self._sync_plan_status(plan_id)

    # ── Internals ─────────────────────────────────────────────────────────────

    async def _load_project(self, project_id: int) -> models.Project:
        result = await self.db.execute(
            select(models.Project).where(models.Project.id == project_id)
        )
        project = result.scalars().first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        return project

    async def _fetch_task_context(self, project_id: int) -> list[dict]:
        result = await self.db.execute(
            select(models.Task).where(models.Task.project_id == project_id)
        )
        tasks = result.scalars().all()
        return [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status.value,
                "priority": t.priority.value,
            }
            for t in tasks
        ]

    async def _resolve_task(
        self,
        task_spec: dict,
        project_id: int,
        user_id: int,
    ) -> int | None:
        action = task_spec.get("action")

        if action == "link":
            task_id = task_spec.get("task_id")
            if task_id:
                result = await self.db.execute(
                    select(models.Task).where(
                        models.Task.id == task_id,
                        models.Task.project_id == project_id,
                    )
                )
                task = result.scalars().first()
                return task.id if task else None
            return None

        if action == "create":
            priority_val = task_spec.get("priority", "medium")
            try:
                priority = models.TaskPriority(int(priority_val))
            except (ValueError, TypeError):
                priority_map = {"low": 1, "medium": 2, "high": 3, "urgent": 4}
                priority = models.TaskPriority(priority_map.get(str(priority_val).lower(), 2))

            task = models.Task(
                project_id=project_id,
                title=task_spec.get("title", "Untitled task"),
                description=task_spec.get("description"),
                priority=priority,
                status=models.TaskStatus.TODO,
            )
            self.db.add(task)
            await self.db.flush()
            return task.id

        return None

    async def _reload(self, plan_id: int) -> models.Plan:
        result = await self.db.execute(
            select(models.Plan)
            .options(
                joinedload(models.Plan.project),
                selectinload(models.Plan.steps).joinedload(models.PlanStep.linked_task),
            )
            .where(models.Plan.id == plan_id)
        )
        plan = result.unique().scalars().first()
        if not plan:
            raise ValueError(f"Plan {plan_id} not found after save")
        return plan

    async def _sync_task_from_step(self, step: models.PlanStep) -> None:
        """When a step status changes, push the equivalent status to its linked task."""
        STEP_TO_TASK: dict[str, str] = {
            "in_progress": "in_progress",
            "completed": "completed",
            "pending": "todo",
        }
        target = STEP_TO_TASK.get(step.status.value)
        if not target or not step.linked_task_id:
            return
        result = await self.db.execute(
            select(models.Task).where(models.Task.id == step.linked_task_id)
        )
        task = result.scalars().first()
        if task and task.status.value != target:
            task.status = models.TaskStatus(target)
            await self.db.commit()

    async def _sync_plan_status(self, plan_id: int) -> None:
        result = await self.db.execute(
            select(models.PlanStep).where(models.PlanStep.plan_id == plan_id)
        )
        steps = result.scalars().all()
        if not steps:
            return
        terminal = {StepStatus.COMPLETED, StepStatus.SKIPPED}
        if all(s.status in terminal for s in steps):
            await self.db.execute(
                select(models.Plan).where(models.Plan.id == plan_id)
            )
            plan_result = await self.db.execute(
                select(models.Plan).where(models.Plan.id == plan_id)
            )
            plan = plan_result.scalars().first()
            if plan and plan.status == PlanStatus.ACTIVE:
                plan.status = PlanStatus.COMPLETED
                await self.db.commit()
