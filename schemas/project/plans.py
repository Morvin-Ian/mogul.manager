import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from models.plans import PlanStatus, StepPriority, StepStatus

# Strips any leaked numeric IDs from AI-generated text fields.
# Catches patterns like: id=66, id: 66, task_id=5, task id 42, (id=66)
_ID_RE = re.compile(
    r'\(?\b(?:task[_\s-]?id|step[_\s-]?id|id)\s*[=:]\s*\d+\b\)?',
    re.IGNORECASE,
)


def _clean(value: str | None) -> str | None:
    if not value:
        return value
    cleaned = _ID_RE.sub('', value).strip()
    # Collapse double spaces left behind after removal
    cleaned = re.sub(r'  +', ' ', cleaned)
    return cleaned or None


class PlanCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    project_id: int


class PlanUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: PlanStatus | None = None


class StepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    plan_id: int
    title: str
    description: str | None
    step_order: int
    priority: StepPriority
    status: StepStatus
    dependencies: list | None
    linked_task_id: int | None
    linked_task_uuid: str | None
    linked_task_title: str | None
    agent_notes: str | None
    created_at: datetime
    updated_at: datetime
    warning: str | None = None   # populated by the update endpoint when relevant

    @field_validator('title', 'description', 'agent_notes', mode='before')
    @classmethod
    def strip_ids(cls, v: str | None) -> str | None:
        return _clean(v)


class StepUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: StepStatus | None = None
    priority: StepPriority | None = None
    linked_task_id: int | None = None
    agent_notes: str | None = None


class StepCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: StepPriority = StepPriority.MEDIUM
    step_order: int | None = None


class PlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    project_id: int
    project_title: str | None
    user_id: int
    title: str
    description: str | None
    status: PlanStatus
    steps: list[StepRead]
    created_at: datetime
    updated_at: datetime
