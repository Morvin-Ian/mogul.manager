from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskDependencyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    title: str
    status: str
    priority: int
    assignee_name: str | None = None


class TaskDependencyList(BaseModel):
    depends_on: list[TaskDependencyRead] = []
    blocked_by: list[TaskDependencyRead] = []
