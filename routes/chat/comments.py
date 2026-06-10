from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from database import get_db
from schemas.chat.comments import CommentCreate, CommentRead, CommentUpdate
from services.activity import ActivityService
from services.auth import CurrentUser
from services.chat.comments import CommentService
from services.notifications import NotificationService, emit_notification_event

router = APIRouter(
    prefix="/api/comments",
    tags=["Comments"],
)


async def _verify_task_ownership(task_id: int, user_id: int, db) -> None:
    result = await db.execute(select(models.Task).where(models.Task.id == task_id))
    task = result.scalars().first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    result = await db.execute(
        select(models.Project).where(models.Project.id == task.project_id)
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
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found"
        )
    # Allow workspace owner OR any workspace member
    if workspace.user_id == user_id:
        return
    member_result = await db.execute(
        select(models.WorkspaceMember).where(
            models.WorkspaceMember.workspace_id == workspace.id,
            models.WorkspaceMember.user_id == user_id,
        )
    )
    if not member_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task",
        )


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: CommentCreate,
    current_user: CurrentUser,
    service: Annotated[CommentService, Depends()],
    activity: Annotated[ActivityService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await _verify_task_ownership(comment.task_id, current_user.id, db)
    data = comment.model_dump(exclude_unset=True)
    data["user_id"] = current_user.id
    created = await service.create(data)

    task_result = await db.execute(
        select(models.Task).where(models.Task.id == comment.task_id)
    )
    task = task_result.scalars().first()
    if task:
        project_result = await db.execute(
            select(models.Project).where(models.Project.id == task.project_id)
        )
        proj = project_result.scalars().first()
        await activity.log(
            user_id=current_user.id,
            entity_type="comment",
            entity_id=created.id,
            action="created",
            workspace_id=proj.workspace_id if proj else None,
            project_id=task.project_id,
            task_id=task.id,
            summary=f"commented on \"{task.title}\"",
        )

    # Notify task assignee about the new comment (unless they wrote it)
    task_result = await db.execute(
        select(models.Task).where(models.Task.id == comment.task_id)
    )
    task = task_result.scalars().first()
    if task and task.assigned_to_id and task.assigned_to_id != current_user.id:
        proj_result = await db.execute(select(models.Project.uuid).where(models.Project.id == task.project_id))
        project_uuid = proj_result.scalar() or ""
        notif_svc = NotificationService(db)
        notif = await notif_svc.create_and_notify(
            user_id=task.assigned_to_id,
            notification_type="comment_added",
            title=f"New comment on \"{task.title}\"",
            message=f"{current_user.username} commented on \"{task.title}\": {comment.content[:200]}",
            link=f"{settings.frontend_url}/projects/{project_uuid}?task={task.uuid}",
            metadata_json={
                "task_uuid": task.uuid,
                "task_id": task.id,
                "comment_id": created.id,
            },
        )
        await emit_notification_event(task.assigned_to_id, notif)

    return created


@router.get("", response_model=list[CommentRead])
async def list_comments(
    current_user: CurrentUser,
    service: Annotated[CommentService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    task_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    await _verify_task_ownership(task_id, current_user.id, db)
    return await service.list_by_task(task_id, skip=skip, limit=limit)


@router.get("/{comment_id}", response_model=CommentRead)
async def get_comment(
    comment_id: int,
    current_user: CurrentUser,
    service: Annotated[CommentService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    comment = await service.get_by_id(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    await _verify_task_ownership(comment.task_id, current_user.id, db)
    return comment


@router.patch("/{comment_id}", response_model=CommentRead)
async def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    current_user: CurrentUser,
    service: Annotated[CommentService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    comment = await service.get_by_id(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment",
        )
    return await service.update(comment, comment_update.model_dump(exclude_unset=True))


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: CurrentUser,
    service: Annotated[CommentService, Depends()],
    activity: Annotated[ActivityService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    comment = await service.get_by_id(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment",
        )
    task_result = await db.execute(
        select(models.Task).where(models.Task.id == comment.task_id)
    )
    task = task_result.scalars().first()
    if task:
        await activity.log(
            user_id=current_user.id,
            entity_type="comment",
            entity_id=comment.id,
            action="deleted",
            project_id=task.project_id,
            task_id=task.id,
            summary=f"deleted a comment on \"{task.title}\"",
        )
    await service.delete(comment)
