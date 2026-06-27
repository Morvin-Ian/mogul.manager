from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from models.collaboration import MemberRole
from schemas.project.plans import (
    PlanCreate,
    PlanRead,
    PlanUpdate,
    StepCreate,
    StepRead,
    StepReorder,
    StepUpdate,
)
from services.auth import CurrentUser
from services.project.plans import PlanService
from services.workspace.collaboration import CollaborationService

router = APIRouter(prefix="/api/plans", tags=["Plans"])


async def _get_project_or_404(project_id: int, db: AsyncSession) -> models.Project:
    result = await db.execute(
        select(models.Project).options().where(models.Project.id == project_id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project


async def _get_plan_or_404(plan_id: str, service: PlanService) -> models.Plan:
    plan = await service.get_by_uuid(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found"
        )
    return plan


async def _get_step_or_404(step_id: str, service: PlanService) -> models.PlanStep:
    step = await service.get_step_by_uuid(step_id)
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Step not found"
        )
    return step


def _to_read(plan: models.Plan) -> PlanRead:
    return PlanRead.model_validate(plan)


def _step_to_read(step: models.PlanStep) -> StepRead:
    return StepRead.model_validate(step)


@router.get("", response_model=list[PlanRead])
async def list_plans(
    project_id: Annotated[int, Query()],
    current_user: CurrentUser,
    service: Annotated[PlanService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[PlanRead]:
    project = await _get_project_or_404(project_id, db)
    await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )
    plans = await service.list_by_project(project_id)
    return [_to_read(p) for p in plans]


@router.post("", response_model=PlanRead, status_code=status.HTTP_201_CREATED)
async def create_plan(
    payload: PlanCreate,
    current_user: CurrentUser,
    service: Annotated[PlanService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlanRead:
    project = await _get_project_or_404(payload.project_id, db)
    await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )
    plan = await service.create(
        project_id=payload.project_id,
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
    )
    return _to_read(plan)


@router.get("/{plan_id}", response_model=PlanRead)
async def get_plan(
    plan_id: str,
    current_user: CurrentUser,
    service: Annotated[PlanService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlanRead:
    plan = await _get_plan_or_404(plan_id, service)
    project = await _get_project_or_404(plan.project_id, db)
    await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )
    return _to_read(plan)


@router.patch("/{plan_id}", response_model=PlanRead)
async def update_plan(
    plan_id: str,
    payload: PlanUpdate,
    current_user: CurrentUser,
    service: Annotated[PlanService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlanRead:
    plan = await _get_plan_or_404(plan_id, service)
    project = await _get_project_or_404(plan.project_id, db)
    await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )
    updated = await service.update(plan, payload.model_dump(exclude_unset=True))
    return _to_read(updated)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: str,
    current_user: CurrentUser,
    service: Annotated[PlanService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    plan = await _get_plan_or_404(plan_id, service)
    project = await _get_project_or_404(plan.project_id, db)
    await collab.require_access(project.workspace_id, current_user.id, min_role="admin")
    await service.delete(plan)


@router.post(
    "/{plan_id}/steps", response_model=PlanRead, status_code=status.HTTP_201_CREATED
)
async def add_step(
    plan_id: str,
    payload: StepCreate,
    current_user: CurrentUser,
    service: Annotated[PlanService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlanRead:
    plan = await _get_plan_or_404(plan_id, service)
    project = await _get_project_or_404(plan.project_id, db)
    await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )
    updated_plan = await service.add_step(
        plan=plan,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        step_order=payload.step_order,
    )
    return _to_read(updated_plan)


@router.patch("/{plan_id}/steps/{step_id}", response_model=StepRead)
async def update_step(
    plan_id: str,
    step_id: str,
    payload: StepUpdate,
    current_user: CurrentUser,
    service: Annotated[PlanService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StepRead:
    plan = await _get_plan_or_404(plan_id, service)
    project = await _get_project_or_404(plan.project_id, db)
    member = await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )
    step = await _get_step_or_404(step_id, service)
    if step.plan_id != plan.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Step not found"
        )

    member_count = await collab.member_count(project.workspace_id)
    is_solo = member_count <= 1
    warning: str | None = None

    data = payload.model_dump(exclude_unset=True)
    new_step_status = data.get("status")

    # Members can only toggle between pending ↔ in_progress.
    # Completed and skipped require admin/owner (mirrors the task review → completed rule).
    if not is_solo and new_step_status and member.role == MemberRole.member:
        MEMBER_STEP_ALLOWED: dict[str, set[str]] = {
            "pending": {"in_progress"},
            "in_progress": {"pending"},
        }
        allowed = MEMBER_STEP_ALLOWED.get(step.status.value, set())
        if new_step_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Only admins and owners can mark steps as Completed or Skipped. "
                    "As an assignee you can move steps between Pending and In Progress."
                ),
            )

    # In a multi-member workspace, check permissions against the linked task
    if not is_solo and step.linked_task_id and new_step_status:
        result = await db.execute(
            select(models.Task).where(models.Task.id == step.linked_task_id)
        )
        linked_task = result.scalars().first()

        if linked_task:
            if linked_task.assigned_to_id is None:
                # Task exists but has no assignee — warn admin, block member
                if member.role == MemberRole.member:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=(
                            f'The linked task "{linked_task.title}" has no assignee. '
                            "Ask an admin to assign it before changing this step's status."
                        ),
                    )
                # Admin/owner: allow but attach warning
                warning = (
                    f'The linked task "{linked_task.title}" has no assignee. '
                    "Consider assigning it so someone is accountable for this step."
                )
            elif (
                member.role == MemberRole.member
                and linked_task.assigned_to_id != current_user.id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f'The linked task "{linked_task.title}" is assigned to someone else. '
                        "Only the assignee, admins, and owners can update this step's status."
                    ),
                )

    updated = await service.update_step(step, data)
    result_schema = _step_to_read(updated)
    if warning:
        result_schema.warning = warning
    return result_schema


@router.post("/{plan_id}/steps/reorder", response_model=PlanRead)
async def reorder_steps(
    plan_id: str,
    payload: list[StepReorder],
    current_user: CurrentUser,
    service: Annotated[PlanService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlanRead:
    plan = await _get_plan_or_404(plan_id, service)
    project = await _get_project_or_404(plan.project_id, db)
    await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )
    pairs = [(s.step_id, s.new_order) for s in payload]
    updated = await service.reorder_steps(plan, pairs)
    return _to_read(updated)


@router.delete("/{plan_id}/steps/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_step(
    plan_id: str,
    step_id: str,
    current_user: CurrentUser,
    service: Annotated[PlanService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    plan = await _get_plan_or_404(plan_id, service)
    project = await _get_project_or_404(plan.project_id, db)
    await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )
    step = await _get_step_or_404(step_id, service)
    if step.plan_id != plan.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Step not found"
        )
    await service.delete_step(step)
