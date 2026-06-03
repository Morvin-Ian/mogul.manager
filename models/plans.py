from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Integer, String, Text, inspect
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import TimestampedModel

if TYPE_CHECKING:
    from .projects import Project
    from .tasks import Task


class PlanStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class StepPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Plan(TimestampedModel):
    __tablename__ = "plans"

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[PlanStatus] = mapped_column(
        SQLEnum(PlanStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=PlanStatus.ACTIVE,
        nullable=False,
    )

    project: Mapped["Project"] = relationship("Project", back_populates="plans")
    steps: Mapped[list["PlanStep"]] = relationship(
        "PlanStep",
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="PlanStep.step_order",
    )

    @property
    def project_title(self) -> str | None:
        try:
            if "project" in inspect(self).unloaded:
                return None
        except Exception:
            pass
        return self.project.title if self.project else None


class PlanStep(TimestampedModel):
    __tablename__ = "plan_steps"

    plan_id: Mapped[int] = mapped_column(
        ForeignKey("plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    step_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    priority: Mapped[StepPriority] = mapped_column(
        SQLEnum(StepPriority, values_callable=lambda obj: [e.value for e in obj]),
        default=StepPriority.MEDIUM,
        nullable=False,
    )
    status: Mapped[StepStatus] = mapped_column(
        SQLEnum(StepStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=StepStatus.PENDING,
        nullable=False,
    )
    dependencies: Mapped[list | None] = mapped_column(JSON, default=list, nullable=True)
    linked_task_id: Mapped[int | None] = mapped_column(
        ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True
    )
    agent_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="steps")
    linked_task: Mapped["Task | None"] = relationship(
        "Task", foreign_keys=[linked_task_id]
    )

    @property
    def linked_task_uuid(self) -> str | None:
        try:
            if "linked_task" in inspect(self).unloaded:
                return None
        except Exception:
            pass
        return self.linked_task.uuid if self.linked_task else None

    @property
    def linked_task_title(self) -> str | None:
        try:
            if "linked_task" in inspect(self).unloaded:
                return None
        except Exception:
            pass
        return self.linked_task.title if self.linked_task else None
