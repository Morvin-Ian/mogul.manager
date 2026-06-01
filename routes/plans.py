from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

import models
from agents.deepseek import DeepSeekAgent as PlannerAgent
from schemas.plans import PlanCreate, PlanDetail, PlanStepUpdate, PlanUpdate
from schemas.plans import PlanStepRead
from services.auth import CurrentUser
from services.plans import PlanService

router = APIRouter(prefix="/api/plans", tags=["Plans"])


@router.get("", response_model=list[PlanDetail])
async def list_plans(
    current_user: CurrentUser,
    svc: Annotated[PlanService, Depends()],
    workspace_id: int | None = Query(None),
    project_id: int | None = Query(None),
):
    if workspace_id is not None:
        plans = await svc.list_by_workspace(workspace_id, current_user.id)
    elif project_id is not None:
        plans = await svc.list_by_project(project_id, current_user.id)
    else:
        plans = await svc.list_accessible(current_user.id)
    return [PlanDetail.model_validate(p) for p in plans]


@router.post("", response_model=PlanDetail, status_code=201)
async def create_plan(
    data: PlanCreate,
    current_user: CurrentUser,
    svc: Annotated[PlanService, Depends()],
):
    # Resolve workspace_id: prefer project's workspace if project_id given
    resolved_workspace_id = data.workspace_id
    project_obj = None
    if data.project_id:
        from sqlalchemy import select as sa_select
        from sqlalchemy.ext.asyncio import AsyncSession
        from database import get_db
        proj_result = await svc.db.execute(
            sa_select(models.Project)
            .where(models.Project.id == data.project_id)
        )
        project_obj = proj_result.scalars().first()
        if project_obj:
            resolved_workspace_id = project_obj.workspace_id

    plan = await svc.create(current_user.id, {
        "title": data.title,
        "description": data.description,
        "workspace_id": resolved_workspace_id,
        "project_id": data.project_id,
        "status": models.PlanStatus.ACTIVE,
    })

    # Build rich goal context: include project tasks if available
    goal = f"{data.title}. {data.description or ''}".strip()
    if project_obj:
        from sqlalchemy import select as sa_select2
        task_result = await svc.db.execute(
            sa_select2(models.Task)
            .where(models.Task.project_id == project_obj.id)
            .limit(30)
        )
        tasks = list(task_result.scalars().all())
        task_lines = "\n".join(
            f"  - {t.title} [{t.status.value}]" for t in tasks
        ) if tasks else "  (no tasks yet)"
        goal += (
            f"\n\nProject context: {project_obj.title}"
            f"\nProject status: {project_obj.status.value}"
            + (f"\nProject description: {project_obj.description}" if project_obj.description else "")
            + f"\nExisting tasks:\n{task_lines}"
        )

    planner = PlannerAgent()
    raw_steps = await planner.decompose(goal)

    saved: list[models.PlanStep] = []
    for i, raw in enumerate(raw_steps):
        step = await svc.create_step({
            "plan_id": plan.id,
            "title": raw.get("title", f"Step {i + 1}"),
            "description": raw.get("description"),
            "priority": raw.get("priority", "medium"),
            "status": models.StepStatus.PENDING,
            "step_order": i,
            "dependencies": [],
        })
        saved.append(step)

    for i, raw in enumerate(raw_steps):
        dep_ids = [saved[j].id for j in raw.get("depends_on", []) if 0 <= j < len(saved)]
        if dep_ids:
            saved[i].dependencies = dep_ids
            await svc.db.commit()

    plan = await svc.get_detail(plan.id)
    return PlanDetail.model_validate(plan)


@router.get("/{plan_id}", response_model=PlanDetail)
async def get_plan(
    plan_id: str,
    current_user: CurrentUser,
    svc: Annotated[PlanService, Depends()],
):
    plan = await svc.get_detail_by_uuid(plan_id)
    if not plan or plan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plan not found")
    return PlanDetail.model_validate(plan)


@router.patch("/{plan_id}", response_model=PlanDetail)
async def update_plan(
    plan_id: str,
    data: PlanUpdate,
    current_user: CurrentUser,
    svc: Annotated[PlanService, Depends()],
):
    plan = await svc.get_by_id(plan_id)
    if not plan or plan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plan not found")
    await svc.update(plan, data.model_dump(exclude_unset=True))
    plan = await svc.get_detail_by_uuid(plan_id)
    return PlanDetail.model_validate(plan)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: str,
    current_user: CurrentUser,
    svc: Annotated[PlanService, Depends()],
):
    plan = await svc.get_by_uuid(plan_id)
    if not plan or plan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plan not found")
    await svc.delete(plan)


@router.patch("/{plan_id}/steps/{step_id}", response_model=PlanStepRead)
async def update_step(
    plan_id: str,
    step_id: str,
    data: PlanStepUpdate,
    current_user: CurrentUser,
    svc: Annotated[PlanService, Depends()],
):
    plan = await svc.get_by_id(plan_id)
    if not plan or plan.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Plan not found")
    step = await svc.get_step_by_uuid(step_id)
    if not step or step.plan_id != plan.id:
        raise HTTPException(status_code=404, detail="Step not found")
    step = await svc.update_step(step, data.model_dump(exclude_unset=True))
    return PlanStepRead.model_validate(step)
