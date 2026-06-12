from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.tasks import TaskPriority, TaskStatus
from schemas.tags import TagRead


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_agent: str | None = None
    assigned_to_id: int | None = None
    parent_task_id: int | None = None
    metadata_json: dict | None = None
    estimated_hours: int | None = None
    actual_hours: int | None = None
    due_date: datetime | None = None


class TaskCreate(TaskBase):
    project_id: int
    assigned_to_email: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assigned_agent: str | None = None
    assigned_to_id: int | None = None
    assigned_to_email: str | None = None
    parent_task_id: int | None = None
    metadata_json: dict | None = None
    estimated_hours: int | None = None
    actual_hours: int | None = None
    due_date: datetime | None = None


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    project_uuid: str | None = None
    project_id: int
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    assignee_name: str | None = None
    assignee_avatar_url: str | None = None
    position: int | None = None
    tags: list[TagRead] = []
    comment_count: int = 0
