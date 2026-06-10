from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import models
from database import get_db
from schemas.dependencies import TaskDependencyList, TaskDependencyRead
from services.activity import ActivityService
from services.auth import CurrentUser
from services.project.tasks import TaskService
from services.workspace.collaboration import CollaborationService

router = APIRouter(
    prefix="/api/tasks/{task_id}/dependencies",
    tags=["Task Dependencies"],
)


async def _get_task_or_404(task_id: str, service: TaskService) -> models.Task:
    task = await service.get_by_uuid(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def _to_dep_read(task: models.Task) -> TaskDependencyRead:
    return TaskDependencyRead(
        id=task.id,
        uuid=task.uuid,
        title=task.title,
        status=task.status.value if hasattr(task.status, "value") else task.status,
        priority=task.priority.value if hasattr(task.priority, "value") else task.priority,
        assignee_name=task.assignee_name,
    )


@router.get("", response_model=TaskDependencyList)
async def list_dependencies(
    task_id: str,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await _get_task_or_404(task_id, service)
    project = await _get_project_or_404(task.project_id, db)
    await collab.require_access(project.workspace_id, current_user.id, min_role="member")

    # Load dependencies and dependent tasks with joins
    result = await db.execute(
        select(models.Task)
        .where(models.Task.id == task.id)
        .options(
            joinedload(models.Task.dependencies).joinedload(models.Task.assignee),
            joinedload(models.Task.dependent_tasks).joinedload(models.Task.assignee),
        )
    )
    t = result.unique().scalars().first()

    return TaskDependencyList(
        depends_on=[_to_dep_read(d) for d in (t.dependencies if t else [])],
        blocked_by=[_to_dep_read(d) for d in (t.dependent_tasks if t else [])],
    )


@router.post("/{dependency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_dependency(
    task_id: str,
    dependency_id: str,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    activity: Annotated[ActivityService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await _get_task_or_404(task_id, service)
    dep_task = await _get_task_or_404(dependency_id, service)

    if task.project_id != dep_task.project_id:
        raise HTTPException(status_code=400, detail="Dependencies must be in the same project")

    project = await _get_project_or_404(task.project_id, db)
    await collab.require_access(project.workspace_id, current_user.id, min_role="member")

    # Prevent self-dependency
    if task.id == dep_task.id:
        raise HTTPException(status_code=400, detail="A task cannot depend on itself")

    # Detect cycles: walk upstream from dep_task and check if we hit task
    if await _would_create_cycle(db, task.id, dep_task.id):
        raise HTTPException(status_code=400, detail="Adding this dependency would create a cycle")

    result = await db.execute(
        select(models.Task).where(models.Task.id == task.id).options(
            joinedload(models.Task.dependencies)
        )
    )
    t = result.unique().scalars().first()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")

    if dep_task not in t.dependencies:
        t.dependencies.append(dep_task)
        await db.commit()

    await activity.log(
        user_id=current_user.id,
        entity_type="task",
        entity_id=task.id,
        action="dependency_added",
        workspace_id=project.workspace_id,
        project_id=task.project_id,
        task_id=task.id,
        summary=f"added dependency: \"{task.title}\" now depends on \"{dep_task.title}\"",
    )


@router.delete("/{dependency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_dependency(
    task_id: str,
    dependency_id: str,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    activity: Annotated[ActivityService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await _get_task_or_404(task_id, service)
    dep_task = await _get_task_or_404(dependency_id, service)
    project = await _get_project_or_404(task.project_id, db)
    await collab.require_access(project.workspace_id, current_user.id, min_role="member")

    result = await db.execute(
        select(models.Task).where(models.Task.id == task.id).options(
            joinedload(models.Task.dependencies)
        )
    )
    t = result.unique().scalars().first()
    if t and dep_task in t.dependencies:
        t.dependencies.remove(dep_task)
        await db.commit()

    await activity.log(
        user_id=current_user.id,
        entity_type="task",
        entity_id=task.id,
        action="dependency_removed",
        workspace_id=project.workspace_id,
        project_id=task.project_id,
        task_id=task.id,
        summary=f"removed dependency: \"{task.title}\" no longer depends on \"{dep_task.title}\"",
    )


async def _get_project_or_404(project_id: int, db: AsyncSession) -> models.Project:
    result = await db.execute(select(models.Project).where(models.Project.id == project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def _would_create_cycle(db: AsyncSession, task_id: int, new_dep_id: int) -> bool:
    """Check if adding new_dep_id as a dependency of task_id would create a cycle."""
    visited = set()
    stack = [new_dep_id]
    while stack:
        current = stack.pop()
        if current == task_id:
            return True
        if current in visited:
            continue
        visited.add(current)
        result = await db.execute(
            select(models.Task).where(models.Task.id == current).options(
                joinedload(models.Task.dependencies)
            )
        )
        t = result.unique().scalars().first()
        if t:
            for dep in t.dependencies:
                if dep.id not in visited:
                    stack.append(dep.id)
    return False
