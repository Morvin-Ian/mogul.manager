import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import models
from config import settings
from database import get_db
from schemas.project.tasks import TaskCreate, TaskRead, TaskUpdate
from services.auth import CurrentUser
from services.project.tasks import TaskService
from utils.email import send_task_assignment_email

logger = logging.getLogger(__name__)

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


async def _resolve_assignee_email(
    data: dict, db: AsyncSession
) -> dict:
    email = data.pop("assigned_to_email", None)
    if email:
        result = await db.execute(
            select(models.User).where(models.User.email == email)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user found with email '{email}'. The person must be a registered user.",
            )
        data["assigned_to_id"] = user.id
    return data


async def _notify_assignment_background(
    to_email: str,
    assignee_name: str,
    assigned_by_name: str,
    task_title: str,
    task_description: str | None,
    project_name: str,
    priority: str,
    status: str,
    task_id: int,
) -> None:
    task_url = f"{settings.frontend_url}/tasks/{task_id}"
    try:
        await send_task_assignment_email(
            to_email=to_email,
            assignee_name=assignee_name,
            assigned_by_name=assigned_by_name,
            task_title=task_title,
            task_description=task_description,
            project_name=project_name,
            priority=priority,
            status=status,
            task_url=task_url,
        )
    except Exception as exc:
        logger.warning("Failed to send task assignment email to %s: %s", to_email, exc)


async def _schedule_notification(
    bt: BackgroundTasks,
    task: models.Task,
    assigned_by: models.User,
    db: AsyncSession,
) -> None:
    if not task.assigned_to_id:
        return
    result = await db.execute(
        select(models.User).where(models.User.id == task.assigned_to_id)
    )
    assignee = result.scalars().first()
    if not assignee or not assignee.email:
        return
    result = await db.execute(
        select(models.Project)
        .options(joinedload(models.Project.workspace))
        .where(models.Project.id == task.project_id)
    )
    project = result.unique().scalars().first()
    project_name = project.title if project else "Unknown"
    priority_map = {1: "Low", 2: "Medium", 3: "High", 4: "Urgent"}
    bt.add_task(
        _notify_assignment_background,
        to_email=assignee.email,
        assignee_name=assignee.username,
        assigned_by_name=assigned_by.username,
        task_title=task.title,
        task_description=task.description,
        project_name=project_name,
        priority=priority_map.get(task.priority, "Medium"),
        status=task.status,
        task_id=task.id,
    )


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: CurrentUser,
    bt: BackgroundTasks,
    service: Annotated[TaskService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _verify_project_ownership(task.project_id, current_user.id, db)
    data = await _resolve_assignee_email(task.model_dump(exclude_unset=True), db)
    created = await service.create(data)
    await _schedule_notification(bt, created, current_user, db)
    return _to_read(created)


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
    tasks = await service.list_by_project(project_id, skip=skip, limit=limit)
    return [_to_read(t) for t in tasks]


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
    return _to_read(task)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: CurrentUser,
    bt: BackgroundTasks,
    service: Annotated[TaskService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await service.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    await _verify_project_ownership(task.project_id, current_user.id, db)
    was_assigned_to = task.assigned_to_id
    data = await _resolve_assignee_email(
        task_update.model_dump(exclude_unset=True), db
    )
    updated = await service.update(task, data)
    if updated.assigned_to_id and updated.assigned_to_id != was_assigned_to:
        await _schedule_notification(bt, updated, current_user, db)
    return _to_read(updated)


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


def _to_read(task: models.Task) -> TaskRead:
    return TaskRead.model_validate(task)
