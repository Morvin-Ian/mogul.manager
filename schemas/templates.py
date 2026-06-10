from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectTemplateBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ProjectTemplateCreate(ProjectTemplateBase):
    project_id: int


class ProjectTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class ProjectTemplateRead(ProjectTemplateBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    workspace_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class CreateFromTemplate(BaseModel):
    workspace_id: int
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
