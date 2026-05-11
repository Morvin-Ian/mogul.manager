from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from schemas.tasks import TaskCreate, TaskRead, TaskUpdate
from services.auth import CurrentUser
from services.tasks import TaskService

router = APIRouter(
    prefix="/api/tasks",
    tags=["Tasks"],
)


async def _verify_project_ownership(
    project_id: int, user_id: int, db
) -> models.Project:
    result = await db.execute(
        select(models.Project).where(models.Project.id == project_id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    result = await db.execute(
        select(models.Workspace).where(models.Workspace.id == project.workspace_id)
    )
    workspace = result.scalars().first()
    if not workspace or workspace.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project",
        )
    return project


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _verify_project_ownership(task.project_id, current_user.id, db)
    return await service.create(task.model_dump(exclude_unset=True))


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    project_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    await _verify_project_ownership(project_id, current_user.id, db)
    return await service.list_by_project(project_id, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await service.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    await _verify_project_ownership(task.project_id, current_user.id, db)
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await service.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    await _verify_project_ownership(task.project_id, current_user.id, db)
    return await service.update(task, task_update.model_dump(exclude_unset=True))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await service.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    await _verify_project_ownership(task.project_id, current_user.id, db)
    await service.delete(task)
