from typing import Annotated

from fastapi import APIRouter, Depends, Query

from schemas.activity import ActivityLogRead
from services.activity import ActivityService
from services.auth import CurrentUser

router = APIRouter(
    prefix="/api",
    tags=["Activity"],
)


@router.get("/workspaces/{workspace_id}/activity", response_model=list[ActivityLogRead])
async def workspace_activity(
    workspace_id: int,
    current_user: CurrentUser,
    activity_svc: Annotated[ActivityService, Depends()],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return await activity_svc.list_by_workspace(workspace_id, skip=skip, limit=limit)


@router.get("/projects/{project_id}/activity", response_model=list[ActivityLogRead])
async def project_activity(
    project_id: int,
    current_user: CurrentUser,
    activity_svc: Annotated[ActivityService, Depends()],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return await activity_svc.list_by_project(project_id, skip=skip, limit=limit)


@router.get("/tasks/{task_id}/activity", response_model=list[ActivityLogRead])
async def task_activity(
    task_id: int,
    current_user: CurrentUser,
    activity_svc: Annotated[ActivityService, Depends()],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return await activity_svc.list_by_task(task_id, skip=skip, limit=limit)
