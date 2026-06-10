from pydantic import BaseModel


class StatusCount(BaseModel):
    status: str
    count: int


class PriorityCount(BaseModel):
    priority: int
    count: int


class ProjectReport(BaseModel):
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    completion_pct: float
    by_status: list[StatusCount]
    by_priority: list[PriorityCount]


class WorkspaceReport(BaseModel):
    total_projects: int
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    completion_pct: float
    by_status: list[StatusCount]
    member_count: int
