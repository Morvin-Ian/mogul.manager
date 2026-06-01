from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

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
):
    plans = await svc.list_by_user(current_user.id)
    return [PlanDetail.model_validate(p) for p in plans]


@router.post("", response_model=PlanDetail, status_code=201)
async def create_plan(
    data: PlanCreate,
    current_user: CurrentUser,
    svc: Annotated[PlanService, Depends()],
):
    plan = await svc.create(current_user.id, {
        "title": data.title,
        "description": data.description,
        "workspace_id": data.workspace_id,
        "status": models.PlanStatus.ACTIVE,
    })

    planner = PlannerAgent()
    raw_steps = await planner.decompose(f"{data.title}. {data.description or ''}".strip())

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
