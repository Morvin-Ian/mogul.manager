from pydantic import BaseModel, Field

from models.tasks import TaskPriority, TaskStatus


class BulkTaskUpdate(BaseModel):
    task_ids: list[int] = Field(min_length=1, max_length=100)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assigned_to_id: int | None = None
    due_date: str | None = None


class BulkTaskDelete(BaseModel):
    task_ids: list[int] = Field(min_length=1, max_length=100)


class BulkTaskAssign(BaseModel):
    task_ids: list[int] = Field(min_length=1, max_length=100)
    assigned_to_id: int


class TaskReorder(BaseModel):
    uuid: str
    position: int
    status: str | None = None
