import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

import models
from config import settings
from database import get_db
from models.collaboration import MemberRole
from models.plans import StepStatus
from schemas.project.tasks import TaskCreate, TaskRead, TaskUpdate
from services.auth import CurrentUser
from services.notifications import NotificationService, emit_notification_event
from services.project.tasks import TaskService
from services.workspace.collaboration import CollaborationService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/tasks",
    tags=["Tasks"],
)

# Fields a regular member (assignee) is allowed to change on their own task
ASSIGNEE_EDITABLE_FIELDS = {"status", "actual_hours", "metadata_json"}

# Status transitions a member (assignee) is allowed to make
MEMBER_ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "todo": {"in_progress"},
    "in_progress": {"todo", "review"},
    "review": {"todo", "in_progress"},
    "blocked": {"todo", "in_progress", "review"},
}


async def _workspace_is_solo(workspace_id: int, db: AsyncSession) -> bool:
    """Return True when the workspace has only one member (personal workspace)."""
    result = await db.execute(
        select(func.count())
        .select_from(models.WorkspaceMember)
        .where(models.WorkspaceMember.workspace_id == workspace_id)
    )
    return (result.scalar_one() or 0) <= 1


async def _sync_step_from_task(
    task: models.Task, new_status: str, db: AsyncSession
) -> None:
    """When a task status changes, push the equivalent status to any linked plan step."""
    TASK_TO_STEP: dict[str, str] = {
        "in_progress": "in_progress",
        "completed": "completed",
        "todo": "pending",
    }
    target = TASK_TO_STEP.get(new_status)
    if not target:
        return
    result = await db.execute(
        select(models.PlanStep).where(models.PlanStep.linked_task_id == task.id)
    )
    steps = result.scalars().all()
    for step in steps:
        if step.status.value != target:
            step.status = StepStatus(target)
    if steps:
        await db.commit()


async def _get_project_or_404(project_id: int, db: AsyncSession) -> models.Project:
    result = await db.execute(
        select(models.Project).where(models.Project.id == project_id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return project


async def _get_task_or_404(task_id: str, service: TaskService) -> models.Task:
    task = await service.get_by_uuid(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


async def _resolve_assignee_email(data: dict, db: AsyncSession) -> dict:
    email = data.pop("assigned_to_email", None)
    if email:
        result = await db.execute(select(models.User).where(models.User.email == email))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user found with email '{email}'. The person must be a registered user.",
            )
        data["assigned_to_id"] = user.id
    return data


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
    if assignee.id == assigned_by.id:
        return  # don't notify yourself
    result = await db.execute(
        select(models.Project)
        .options(joinedload(models.Project.workspace))
        .where(models.Project.id == task.project_id)
    )
    project = result.unique().scalars().first()
    project_name = project.title if project else "Unknown"

    priority_map = {1: "Low", 2: "Medium", 3: "High", 4: "Urgent"}
    priority_label = priority_map.get(task.priority, "Medium")

    project_uuid = project.uuid if project else ""
    task_url = f"{settings.frontend_url}/projects/{project_uuid}?task={task.uuid}"
    notif_svc = NotificationService(db)

    notif = await notif_svc.create_and_notify(
        user_id=assignee.id,
        notification_type="task_assigned",
        title=f"Task assigned: {task.title}",
        message=f"{assigned_by.username} assigned you \"{task.title}\" in {project_name} (Priority: {priority_label})",
        link=task_url,
        metadata_json={
            "task_uuid": task.uuid,
            "project_id": task.project_id,
            "assigned_by": assigned_by.username,
            "priority": priority_label,
        },
        email_to=assignee.email,
        email_subject=f"Task assigned: {task.title}",
    )
    await emit_notification_event(assignee.id, notif)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: CurrentUser,
    bt: BackgroundTasks,
    service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project = await _get_project_or_404(task.project_id, db)
    member = await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )

    data = await _resolve_assignee_email(task.model_dump(exclude_unset=True), db)

    # Regular members may only assign tasks to themselves
    if member.role == MemberRole.member:
        assigned_to = data.get("assigned_to_id")
        if assigned_to and assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Members can only assign tasks to themselves",
            )

    created = await service.create(data)
    await _schedule_notification(bt, created, current_user, db)
    return _to_read(created)


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    project_id: int | None = Query(None),
    workspace_id: int | None = Query(None),
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    if workspace_id is not None:
        await collab.require_access(workspace_id, current_user.id, min_role="member")
        tasks = await service.list_by_workspace(
            workspace_id, status=status, skip=skip, limit=limit
        )
        return [_to_read(t) for t in tasks]
    if project_id is None:
        raise HTTPException(
            status_code=400, detail="Either project_id or workspace_id is required"
        )
    project = await _get_project_or_404(project_id, db)
    await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )
    tasks = await service.list_by_project(project_id, skip=skip, limit=limit)
    return [_to_read(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: str,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await _get_task_or_404(task_id, service)
    project = await _get_project_or_404(task.project_id, db)
    await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )
    return _to_read(task)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: CurrentUser,
    bt: BackgroundTasks,
    service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await _get_task_or_404(task_id, service)
    project = await _get_project_or_404(task.project_id, db)
    member = await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )
    solo = await _workspace_is_solo(project.workspace_id, db)

    data = task_update.model_dump(exclude_unset=True)

    # Block status changes on unassigned tasks in team workspaces — no role exceptions
    new_status_check = data.get("status")
    if (
        not solo
        and task.assigned_to_id is None
        and new_status_check
        and new_status_check != task.status.value
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "This task has no assignee. Assign it to a team member before changing its status. "
                "Tip: ask AI in Chat to assign tasks to the team automatically."
            ),
        )

    if not solo and member.role == MemberRole.member:
        # Multi-member workspace: regular members may only update tasks assigned to them
        if task.assigned_to_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update tasks assigned to you",
            )
        disallowed = set(data.keys()) - ASSIGNEE_EDITABLE_FIELDS
        if disallowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Members may only change: {', '.join(sorted(ASSIGNEE_EDITABLE_FIELDS))}",
            )
        new_status = data.get("status")
        if new_status and new_status != task.status:
            allowed = MEMBER_ALLOWED_TRANSITIONS.get(task.status, set())
            if new_status not in allowed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only move tasks forward, or move an In Revision task back to an earlier stage.",
                )

    was_assigned_to = task.assigned_to_id
    old_status = task.status.value
    data = await _resolve_assignee_email(data, db)
    updated = await service.update(task, data)
    if updated.assigned_to_id and updated.assigned_to_id != was_assigned_to:
        await _schedule_notification(bt, updated, current_user, db)

    # Sync any linked plan step when status changed
    new_status_val = data.get("status")
    if new_status_val and new_status_val != old_status:
        await _sync_step_from_task(updated, new_status_val, db)

        # Notify assignee of status change (unless they changed it themselves)
        if updated.assigned_to_id and updated.assigned_to_id != current_user.id:
            proj_result = await db.execute(select(models.Project.uuid).where(models.Project.id == updated.project_id))
            project_uuid = proj_result.scalar() or ""
            status_labels = {"todo": "To Do", "in_progress": "In Progress", "review": "In Review", "blocked": "Blocked", "completed": "Completed"}
            notif_svc = NotificationService(db)
            notif = await notif_svc.create_and_notify(
                user_id=updated.assigned_to_id,
                notification_type="task_status_changed",
                title=f"Task status changed: {updated.title}",
                message=f"{current_user.username} moved \"{updated.title}\" from {status_labels.get(old_status, old_status)} to {status_labels.get(new_status_val, new_status_val)}",
                link=f"{settings.frontend_url}/projects/{project_uuid}?task={updated.uuid}",
                metadata_json={"task_uuid": updated.uuid, "old_status": old_status, "new_status": new_status_val},
            )
            await emit_notification_event(updated.assigned_to_id, notif)

    return _to_read(updated)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await _get_task_or_404(task_id, service)
    project = await _get_project_or_404(task.project_id, db)
    # Only admins and owners can delete tasks
    await collab.require_access(project.workspace_id, current_user.id, min_role="admin")
    await service.delete(task)


@router.post("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_task(
    body: dict,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Move a task to a new position (and optionally a new status column)."""
    uuid = body.get("uuid")
    new_position = body.get("position")
    new_status = body.get("status")
    if not uuid or new_position is None:
        raise HTTPException(status_code=400, detail="uuid and position are required")

    task = await _get_task_or_404(uuid, service)
    project = await _get_project_or_404(task.project_id, db)
    member = await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )
    solo = await _workspace_is_solo(project.workspace_id, db)

    # Block unassigned tasks in team workspaces — no role exceptions
    if not solo and task.assigned_to_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "This task has no assignee. Assign it to a team member before moving it. "
                "Tip: ask AI in Chat to assign tasks to the team automatically."
            ),
        )

    if not solo and member.role == MemberRole.member:
        if task.assigned_to_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only move tasks assigned to you",
            )

    old_status = task.status.value
    target_status = new_status or task.status.value
    await service.reorder_task(task, int(new_position), target_status)

    # Sync plan step if status changed via drag
    if target_status != old_status:
        await _sync_step_from_task(task, target_status, db)


def _to_read(task: models.Task) -> TaskRead:
    return TaskRead.model_validate(task)
