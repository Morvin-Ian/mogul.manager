from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from schemas.tags import TagCreate, TagRead, TagUpdate
from services.auth import CurrentUser
from services.tags import TagService
from services.workspace.collaboration import CollaborationService

router = APIRouter(
    prefix="/api",
    tags=["Tags"],
)


async def _require_project_access(
    project_id: int,
    user_id: int,
    db: AsyncSession,
    collab: CollaborationService,
) -> models.Project:
    result = await db.execute(
        select(models.Project).where(models.Project.id == project_id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await collab.require_access(project.workspace_id, user_id, min_role="member")
    return project


async def _require_task_access(
    task_id: int,
    user_id: int,
    db: AsyncSession,
    collab: CollaborationService,
) -> models.Task:
    result = await db.execute(select(models.Task).where(models.Task.id == task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await _require_project_access(task.project_id, user_id, db, collab)
    return task


async def _get_tag_in_project(
    tag_id: int, project_id: int, db: AsyncSession
) -> models.Tag:
    result = await db.execute(select(models.Tag).where(models.Tag.id == tag_id))
    tag = result.scalars().first()
    if not tag or tag.project_id != project_id:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.get("/projects/{project_id}/tags", response_model=list[TagRead])
async def list_tags(
    project_id: int,
    current_user: CurrentUser,
    tag_svc: Annotated[TagService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _require_project_access(project_id, current_user.id, db, collab)
    return await tag_svc.list_by_project(project_id)


@router.post("/projects/{project_id}/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
async def create_tag(
    project_id: int,
    body: TagCreate,
    current_user: CurrentUser,
    tag_svc: Annotated[TagService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _require_project_access(project_id, current_user.id, db, collab)
    return await tag_svc.create(project_id, body.name, body.color)


@router.patch("/projects/{project_id}/tags/{tag_id}", response_model=TagRead)
async def update_tag(
    project_id: int,
    tag_id: int,
    body: TagUpdate,
    current_user: CurrentUser,
    tag_svc: Annotated[TagService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _require_project_access(project_id, current_user.id, db, collab)
    await _get_tag_in_project(tag_id, project_id, db)
    tag = await tag_svc.update(tag_id, body.name, body.color)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.delete("/projects/{project_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    project_id: int,
    tag_id: int,
    current_user: CurrentUser,
    tag_svc: Annotated[TagService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _require_project_access(project_id, current_user.id, db, collab)
    await _get_tag_in_project(tag_id, project_id, db)
    ok = await tag_svc.delete(tag_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tag not found")


@router.post("/tasks/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def attach_tag(
    task_id: int,
    tag_id: int,
    current_user: CurrentUser,
    tag_svc: Annotated[TagService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await _require_task_access(task_id, current_user.id, db, collab)
    await _get_tag_in_project(tag_id, task.project_id, db)
    ok = await tag_svc.attach_to_task(task_id, tag_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task or tag not found")


@router.delete("/tasks/{task_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def detach_tag(
    task_id: int,
    tag_id: int,
    current_user: CurrentUser,
    tag_svc: Annotated[TagService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _require_task_access(task_id, current_user.id, db, collab)
    ok = await tag_svc.detach_from_task(task_id, tag_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task or tag not found")


@router.get("/tasks/{task_id}/tags", response_model=list[TagRead])
async def list_task_tags(
    task_id: int,
    current_user: CurrentUser,
    tag_svc: Annotated[TagService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _require_task_access(task_id, current_user.id, db, collab)
    return await tag_svc.list_task_tags(task_id)
