from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.projects import ProjectStatus


class ProjectBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: ProjectStatus = ProjectStatus.PLANNING
    metadata_json: dict | None = None
    start_date: datetime | None = None
    due_date: datetime | None = None


class ProjectCreate(ProjectBase):
    workspace_id: int


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: ProjectStatus | None = None
    metadata_json: dict | None = None
    start_date: datetime | None = None
    due_date: datetime | None = None
    is_archived: bool | None = None


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    workspace_uuid: str | None = None
    workspace_id: int
    created_by_id: int | None
    ai_summary: str | None
    completed_at: datetime | None
    is_archived: bool
    created_at: datetime
    updated_at: datetime
