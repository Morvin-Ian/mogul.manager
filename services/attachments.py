from __future__ import annotations

import uuid as _uuid_mod
from pathlib import Path
from typing import Annotated

from fastapi import Depends, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

import models
from database import get_db
from services.documents.service import _s3_delete, _s3_upload

MAX_ATTACHMENT_SIZE = 50 * 1024 * 1024  # 50 MB


class AttachmentService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    ALLOWED_EXTENSIONS = frozenset(
        {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".svg",
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".txt",
            ".csv",
            ".zip",
            ".rar",
            ".7z",
            ".tar",
            ".gz",
        }
    )

    ALLOWED_MIMES = frozenset(
        {
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "image/svg+xml",
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "text/plain",
            "text/csv",
            "application/zip",
            "application/x-rar-compressed",
            "application/x-7z-compressed",
            "application/x-tar",
            "application/gzip",
        }
    )

    async def upload(
        self, task_id: int, user_id: int, file: UploadFile
    ) -> models.TaskAttachment:
        ext = Path(file.filename or "file").suffix.lower()
        mime = (file.content_type or "").lower()
        if ext not in self.ALLOWED_EXTENSIONS and mime not in self.ALLOWED_MIMES:
            raise ValueError(f"File type '{ext or mime}' is not allowed.")

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
