from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import TimestampedModel

if TYPE_CHECKING:
    from .projects import Project
    from .tasks import Task
    from .users import User


class PlanStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StepPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Plan(TimestampedModel):
    __tablename__ = "plans"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    workspace_id: Mapped[int | None] = mapped_column(
        ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True
    )
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[PlanStatus] = mapped_column(SQLEnum(PlanStatus), default=PlanStatus.ACTIVE)

    user: Mapped["User"] = relationship("User")
    project: Mapped["Project | None"] = relationship("Project")
    steps: Mapped[list["PlanStep"]] = relationship(
        "PlanStep",
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="PlanStep.step_order",
    )


class PlanStep(TimestampedModel):
    __tablename__ = "plan_steps"

    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[StepPriority] = mapped_column(SQLEnum(StepPriority), default=StepPriority.MEDIUM)
    status: Mapped[StepStatus] = mapped_column(SQLEnum(StepStatus), default=StepStatus.PENDING)
    step_order: Mapped[int] = mapped_column(Integer, default=0)
    dependencies: Mapped[list] = mapped_column(JSON, default=list)
    linked_task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    agent_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="steps")
    linked_task: Mapped["Task | None"] = relationship("Task")

    @property
    def linked_task_uuid(self) -> str | None:
        try:
            from sqlalchemy import inspect as _i
            if 'linked_task' in _i(self).unloaded:
                return None
        except Exception:
            pass
        return self.linked_task.uuid if self.linked_task else None

    @property
    def project_title(self) -> str | None:
        try:
            from sqlalchemy import inspect as _i
            if 'project' in _i(self).unloaded:
                return None
        except Exception:
            pass
        return self.project.title if self.project else None
