import logging
from datetime import datetime
from enum import Enum
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
from schemas.bulk import BulkTaskDelete, BulkTaskUpdate
from schemas.project.tasks import TaskCreate, TaskRead, TaskUpdate
from services.activity import ActivityService
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
        message=f'{assigned_by.username} assigned you "{task.title}" in {project_name} (Priority: {priority_label})',
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
    activity: Annotated[ActivityService, Depends()],
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

    await activity.log(
        user_id=current_user.id,
        entity_type="task",
        entity_id=created.id,
        action="created",
        workspace_id=project.workspace_id,
        project_id=created.project_id,
        task_id=created.id,
        summary=f'created task "{created.title}"',
    )

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
        await _attach_comment_counts(db, tasks)
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
    await _attach_comment_counts(db, tasks)
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
    await _attach_comment_counts(db, [task])
    return _to_read(task)


def _json_safe(v: object) -> object:
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, Enum):
        return v.value
    return v


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: CurrentUser,
    bt: BackgroundTasks,
    service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    activity: Annotated[ActivityService, Depends()],
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

        # Notify relevant parties of status change
        proj_result = await db.execute(
            select(models.Project.uuid).where(models.Project.id == updated.project_id)
        )
        project_uuid = proj_result.scalar() or ""
        status_labels = {
            "todo": "To Do",
            "in_progress": "In Progress",
            "review": "In Review",
            "blocked": "Blocked",
            "completed": "Completed",
        }
        notif_title = f"Task status changed: {updated.title}"
        notif_body = f'{current_user.username} moved "{updated.title}" from {status_labels.get(old_status, old_status)} to {status_labels.get(new_status_val, new_status_val)}'
        notif_link = (
            f"{settings.frontend_url}/projects/{project_uuid}?task={updated.uuid}"
        )
        notif_meta = {
            "task_uuid": updated.uuid,
            "old_status": old_status,
            "new_status": new_status_val,
        }

        # Notify assignee when someone else changes their task status
        if updated.assigned_to_id and updated.assigned_to_id != current_user.id:
            notif_svc = NotificationService(db)
            notif = await notif_svc.create_and_notify(
                user_id=updated.assigned_to_id,
                notification_type="task_status_changed",
                title=notif_title,
                message=notif_body,
                link=notif_link,
                metadata_json=notif_meta,
            )
            await emit_notification_event(updated.assigned_to_id, notif)

        # Notify workspace admins when a member changes task status
        if member.role == MemberRole.member:
            await _notify_workspace_admins(
                workspace_id=project.workspace_id,
                notification_type="task_status_changed",
                title=notif_title,
                message=notif_body,
                link=notif_link,
                metadata_json=notif_meta,
                exclude_user_id=current_user.id,
                db=db,
            )

    changed_fields = {k: _json_safe(v) for k, v in data.items() if v is not None}
    if changed_fields:
        summary_parts = []
        if "status" in changed_fields:
            summary_parts.append(f"changed status to {changed_fields['status']}")
        if "assigned_to_id" in changed_fields:
            summary_parts.append("changed assignee")
        if "title" in changed_fields:
            summary_parts.append("renamed task")
        if "priority" in changed_fields:
            summary_parts.append(f"changed priority to {changed_fields['priority']}")
        if not summary_parts:
            summary_parts.append("updated task")
        await activity.log(
            user_id=current_user.id,
            entity_type="task",
            entity_id=updated.id,
            action="updated",
            workspace_id=project.workspace_id,
            project_id=updated.project_id,
            task_id=updated.id,
            summary=f'{summary_parts[0]} "{updated.title}"',
            changes=changed_fields,
        )

    await _attach_comment_counts(db, [updated])
    return _to_read(updated)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    activity: Annotated[ActivityService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await _get_task_or_404(task_id, service)
    project = await _get_project_or_404(task.project_id, db)
    # Only admins and owners can delete tasks
    await collab.require_access(project.workspace_id, current_user.id, min_role="admin")
    await activity.log(
        user_id=current_user.id,
        entity_type="task",
        entity_id=task.id,
        action="deleted",
        workspace_id=project.workspace_id,
        project_id=task.project_id,
        task_id=task.id,
        summary=f'deleted task "{task.title}"',
    )
    await service.delete(task)


@router.post("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_task(
    body: dict,
    current_user: CurrentUser,
    service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    activity: Annotated[ActivityService, Depends()],
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
        await activity.log(
            user_id=current_user.id,
            entity_type="task",
            entity_id=task.id,
            action="status_changed",
            workspace_id=project.workspace_id,
            project_id=task.project_id,
            task_id=task.id,
            summary=f'moved "{task.title}" from {old_status} to {target_status}',
            changes={"status": {"from": old_status, "to": target_status}},
        )


@router.post("/batch/update", status_code=status.HTTP_204_NO_CONTENT)
async def bulk_update_tasks(
    body: BulkTaskUpdate,
    current_user: CurrentUser,
    collab: Annotated[CollaborationService, Depends()],
    activity: Annotated[ActivityService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Task)
        .where(models.Task.id.in_(body.task_ids))
        .options(joinedload(models.Task.project))
    )
    tasks = list(result.unique().scalars().all())
    if not tasks:
        return

    # All tasks must be in the same project
    project_ids = {t.project_id for t in tasks}
    project = await _get_project_or_404(next(iter(project_ids)), db)
    # All tasks must be accessible (same project) for the operation to proceed
    if len(project_ids) > 1:
        raise HTTPException(
            status_code=400, detail="All tasks must be in the same project"
        )
    member = await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )

    # Mirror the single-task rules so bulk ops can't bypass them
    solo = await _workspace_is_solo(project.workspace_id, db)
    if not solo and member.role == MemberRole.member:
        not_mine = [t for t in tasks if t.assigned_to_id != current_user.id]
        if not_mine:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only bulk-update tasks assigned to you",
            )
    if body.status is not None and not solo and body.assigned_to_id is None:
        unassigned = [t for t in tasks if t.assigned_to_id is None]
        if unassigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Some tasks have no assignee. Assign them before changing status.",
            )

    update_data = {}
    if body.status is not None:
        update_data["status"] = (
            body.status.value if hasattr(body.status, "value") else body.status
        )
    if body.priority is not None:
        update_data["priority"] = (
            body.priority.value if hasattr(body.priority, "value") else body.priority
        )
    if body.assigned_to_id is not None:
        update_data["assigned_to_id"] = body.assigned_to_id
    if body.due_date is not None:
        update_data["due_date"] = body.due_date

    if not update_data:
        return

    for t in tasks:
        for key, value in update_data.items():
            setattr(t, key, value)
    await db.commit()

    await activity.log(
        user_id=current_user.id,
        entity_type="task",
        entity_id=0,
        action="bulk_updated",
        workspace_id=project.workspace_id,
        project_id=project.id,
        summary=f"bulk updated {len(tasks)} tasks",
        changes={"task_ids": body.task_ids, **update_data},
    )


@router.post("/batch/delete", status_code=status.HTTP_204_NO_CONTENT)
async def bulk_delete_tasks(
    body: BulkTaskDelete,
    current_user: CurrentUser,
    collab: Annotated[CollaborationService, Depends()],
    activity: Annotated[ActivityService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Task).where(models.Task.id.in_(body.task_ids))
    )
    tasks = list(result.scalars().all())
    if not tasks:
        return

    project_ids = {t.project_id for t in tasks}
    project = await _get_project_or_404(next(iter(project_ids)), db)
    if len(project_ids) > 1:
        raise HTTPException(
            status_code=400, detail="All tasks must be in the same project"
        )
    await collab.require_access(project.workspace_id, current_user.id, min_role="admin")

    for t in tasks:
        await db.delete(t)
    await db.commit()

    await activity.log(
        user_id=current_user.id,
        entity_type="task",
        entity_id=0,
        action="bulk_deleted",
        workspace_id=project.workspace_id,
        project_id=project.id,
        summary=f"bulk deleted {len(tasks)} tasks",
        changes={"task_ids": body.task_ids},
    )


def _to_read(task: models.Task) -> TaskRead:
    # model_validate with from_attributes=True may not pick up transient
    # attributes set by _attach_comment_counts, so we explicitly supply it.
    result = TaskRead.model_validate(task)
    cc = getattr(task, "comment_count", None)
    if cc is not None:
        result.comment_count = cc
    return result


async def _notify_workspace_admins(
    workspace_id: int,
    notification_type: str,
    title: str,
    message: str,
    link: str,
    metadata_json: dict | None,
    exclude_user_id: int,
    db: AsyncSession,
) -> None:
    """Send a notification to all admin/owner members of a workspace, excluding a given user."""
    result = await db.execute(
        select(models.WorkspaceMember).where(
            models.WorkspaceMember.workspace_id == workspace_id,
            models.WorkspaceMember.role.in_([MemberRole.admin, MemberRole.owner]),
        )
    )
    admins = result.scalars().all()
    notif_svc = NotificationService(db)
    for admin in admins:
        if admin.user_id == exclude_user_id:
            continue
        notif = await notif_svc.create(
            user_id=admin.user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            metadata_json=metadata_json,
        )
        await emit_notification_event(admin.user_id, notif)


async def _attach_comment_counts(db: AsyncSession, tasks: list[models.Task]) -> None:
    """Set a transient comment_count attribute that TaskRead picks up."""
    ids = [t.id for t in tasks]
    if not ids:
        return
    result = await db.execute(
        select(models.Comment.task_id, func.count(models.Comment.id))
        .where(models.Comment.task_id.in_(ids))
        .group_by(models.Comment.task_id)
    )
    counts = dict(result.all())
    for t in tasks:
        t.comment_count = counts.get(t.id, 0)
