from __future__ import annotations

import uuid as _uuid_mod
from pathlib import Path
from typing import Annotated

from fastapi import Depends, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

import models
from config import settings
from database import get_db
from services.documents.service import _s3_delete, _s3_upload

MAX_ATTACHMENT_SIZE = 50 * 1024 * 1024  # 50 MB


class AttachmentService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def upload(
        self, task_id: int, user_id: int, file: UploadFile
    ) -> models.TaskAttachment:
        content = await file.read()
        if len(content) > MAX_ATTACHMENT_SIZE:
            raise ValueError("File exceeds the 50 MB size limit.")

        ext = Path(file.filename or "file").suffix.lower()
        storage_key = f"attachments/{_uuid_mod.uuid4().hex}{ext}"

        await run_in_threadpool(_s3_upload, content, storage_key)

        attachment = models.TaskAttachment(
            task_id=task_id,
            user_id=user_id,
            original_filename=file.filename or "unnamed",
            file_size=len(content),
            mime_type=file.content_type or "application/octet-stream",
            storage_key=storage_key,
        )
        self.db.add(attachment)
        await self.db.commit()
        await self.db.refresh(attachment)
        return attachment

    async def list_by_task(
        self, task_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[list[models.TaskAttachment], int]:
        total_q = await self.db.execute(
            select(func.count(models.TaskAttachment.id)).where(
                models.TaskAttachment.task_id == task_id
            )
        )
        total = total_q.scalar() or 0

        result = await self.db.execute(
            select(models.TaskAttachment)
            .where(models.TaskAttachment.task_id == task_id)
            .order_by(models.TaskAttachment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def delete(self, attachment_id: int, user_id: int) -> bool:
        result = await self.db.execute(
            select(models.TaskAttachment).where(
                models.TaskAttachment.id == attachment_id,
                models.TaskAttachment.user_id == user_id,
            )
        )
        attachment = result.scalars().first()
        if not attachment:
            return False

        try:
            await run_in_threadpool(_s3_delete, attachment.storage_key)
        except Exception:
            pass

        await self.db.delete(attachment)
        await self.db.commit()
        return True
