import logging
from typing import Annotated

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
from config import settings
from database import get_db
from schemas.attachments import AttachmentList, AttachmentRead
from services.attachments import AttachmentService
from services.auth import CurrentUser
from services.notifications import NotificationService, emit_notification_event
from services.project.tasks import TaskService
from services.workspace.collaboration import CollaborationService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/tasks/{task_id}/attachments",
    tags=["Task Attachments"],
)


async def _get_task_or_404(task_id: str, service: TaskService) -> models.Task:
    task = await service.get_by_uuid(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


async def _get_project_or_404(project_id: int, db: AsyncSession) -> models.Project:
    result = await db.execute(
        select(models.Project).where(models.Project.id == project_id)
    )
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=AttachmentList)
async def list_attachments(
    task_id: str,
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    attachment: Annotated[AttachmentService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    task = await _get_task_or_404(task_id, task_service)
    project = await _get_project_or_404(task.project_id, db)
    await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )

    items, total = await attachment.list_by_task(task.id, skip=skip, limit=limit)
    return AttachmentList(items=items, total=total)


@router.post("", response_model=AttachmentRead, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    task_id: str,
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    attachment: Annotated[AttachmentService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
):
    task = await _get_task_or_404(task_id, task_service)
    project = await _get_project_or_404(task.project_id, db)
    await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )

    try:
        att = await attachment.upload(task.id, current_user.id, file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except (BotoCoreError, ClientError) as exc:
        logger.error("Attachment upload to storage failed: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="File storage is temporarily unavailable. Please try again.",
        )

    result = await db.execute(
        select(models.WorkspaceMember).where(
            models.WorkspaceMember.workspace_id == project.workspace_id,
            models.WorkspaceMember.user_id != current_user.id,
        )
    )
    members = result.scalars().all()
    notif_svc = NotificationService(db)
    project_uuid = project.uuid
    notif_link = f"{settings.frontend_url}/projects/{project_uuid}?task={task.uuid}"
    for m in members:
        notif = await notif_svc.create(
            user_id=m.user_id,
            notification_type="attachment_uploaded",
            title=f'Attachment added to "{task.title}"',
            message=f'{current_user.username} attached "{att.original_filename}" to task "{task.title}" in {project.title}',
            link=notif_link,
            metadata_json={
                "task_uuid": task.uuid,
                "project_id": task.project_id,
                "project_uuid": project_uuid,
                "attachment_id": att.id,
            },
        )
        await emit_notification_event(m.user_id, notif)

    return att


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    task_id: str,
    attachment_id: int,
    current_user: CurrentUser,
    task_service: Annotated[TaskService, Depends()],
    collab: Annotated[CollaborationService, Depends()],
    attachment: Annotated[AttachmentService, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await _get_task_or_404(task_id, task_service)
    project = await _get_project_or_404(task.project_id, db)
    await collab.require_access(
        project.workspace_id, current_user.id, min_role="member"
    )

    ok = await attachment.delete(attachment_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Attachment not found")
