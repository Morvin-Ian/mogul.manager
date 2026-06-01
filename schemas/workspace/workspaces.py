from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    settings: dict | None = None


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    settings: dict | None = None
    is_archived: bool | None = None


class WorkspaceRead(WorkspaceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    user_id: int
    is_archived: bool
    created_at: datetime
    updated_at: datetime
