from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PlanStatusType = Literal["draft", "active", "completed", "cancelled"]
StepStatusType = Literal["pending", "running", "completed", "failed", "skipped"]
StepPriorityType = Literal["low", "medium", "high", "urgent"]


class PlanStepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    plan_id: int
    title: str
    description: str | None
    priority: str
    status: str
    step_order: int
    dependencies: list[int]
    linked_task_id: int | None
    agent_notes: str | None
    linked_task_uuid: str | None = None
    created_at: datetime
    updated_at: datetime


class PlanStepUpdate(BaseModel):
    status: StepStatusType | None = None
    agent_notes: str | None = None
    linked_task_id: int | None = None


class PlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    user_id: int
    workspace_id: int | None
    project_id: int | None = None
    project_title: str | None = None
    title: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class PlanDetail(PlanRead):
    steps: list[PlanStepRead] = []

    @property
    def progress(self) -> int:
        if not self.steps:
            return 0
        done = sum(1 for s in self.steps if s.status in ("completed", "skipped"))
        return round(done / len(self.steps) * 100)


class PlanCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    project_id: int | None = None
    workspace_id: int | None = None


class PlanUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: PlanStatusType | None = None
    workspace_id: int | None = None
    project_id: int | None = None
