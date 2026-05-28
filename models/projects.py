from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database import Base

if TYPE_CHECKING:
    from .tasks import Task
    from .users import User
    from .workspaces import Workspace


class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
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
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )

    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        back_populates="projects",
    )
    creator: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[created_by_id],
    )

    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )
