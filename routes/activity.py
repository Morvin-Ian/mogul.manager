from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from models.collaboration import WorkspaceMember
from models.projects import Project
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
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )
    if not result.scalars().first():
        raise HTTPException(403, "You are not a member of this workspace")
    return await activity_svc.list_by_workspace(workspace_id, skip=skip, limit=limit)


@router.get("/projects/{project_id}/activity", response_model=list[ActivityLogRead])
async def project_activity(
    project_id: int,
    current_user: CurrentUser,
    activity_svc: Annotated[ActivityService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    proj_result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = proj_result.scalars().first()
    if not project:
        raise HTTPException(404, "Project not found")
    member_result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == project.workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )
    if not member_result.scalars().first():
        raise HTTPException(403, "You are not a member of this workspace")
    return await activity_svc.list_by_project(project_id, skip=skip, limit=limit)


@router.get("/tasks/{task_id}/activity", response_model=list[ActivityLogRead])
async def task_activity(
    task_id: int,
    current_user: CurrentUser,
    activity_svc: Annotated[ActivityService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    task_result = await db.execute(
        select(models.Task).where(models.Task.id == task_id)
    )
    task = task_result.scalars().first()
    if not task:
        raise HTTPException(404, "Task not found")
    proj_result = await db.execute(
        select(Project).where(Project.id == task.project_id)
    )
    project = proj_result.scalars().first()
    if project:
        member_result = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == project.workspace_id,
                WorkspaceMember.user_id == current_user.id,
            )
        )
        if not member_result.scalars().first():
            raise HTTPException(403, "You are not a member of this workspace")
    return await activity_svc.list_by_task(task_id, skip=skip, limit=limit)
