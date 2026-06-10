from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config import settings
from models.base import TimestampedModel

if TYPE_CHECKING:
    from .tasks import Task
    from .users import User


class TaskAttachment(TimestampedModel):
    __tablename__ = "task_attachments"

    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(1000), nullable=False)

    task: Mapped["Task"] = relationship("Task", back_populates="attachments")
    uploader: Mapped["User"] = relationship("User")

    @property
    def url(self) -> str:
        return f"https://{settings.s3_custom_domain}/{self.storage_key}"

    @property
    def uploader_name(self) -> str | None:
        return self.uploader.username if self.uploader else None
