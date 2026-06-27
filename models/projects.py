from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, inspect
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import TimestampedModel

if TYPE_CHECKING:
    from .milestones import Milestone
    from .plans import Plan
    from .tags import Tag
    from .tasks import Task
    from .users import User
    from .workspaces import Workspace


class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(TimestampedModel):
    __tablename__ = "projects"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus), default=ProjectStatus.PLANNING
    )
    workspace_id: Mapped[int] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    ai_summary: Mapped[str] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="projects")
    creator: Mapped["User | None"] = relationship("User", foreign_keys=[created_by_id])
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    plans: Mapped[list["Plan"]] = relationship(
        "Plan",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    milestones: Mapped[list["Milestone"]] = relationship(
        "Milestone",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    @property
    def workspace_uuid(self) -> str | None:
        try:
            if 'workspace' in inspect(self).unloaded:
                return None
        except AttributeError:
            return None
        return self.workspace.uuid if self.workspace else None

    @property
    def workspace_title(self) -> str | None:
        try:
            if 'workspace' in inspect(self).unloaded:
                return None
        except AttributeError:
            return None
        return self.workspace.title if self.workspace else None
