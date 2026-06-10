from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.milestones import MilestoneStatus


class MilestoneBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None


class MilestoneCreate(MilestoneBase):
    pass


class MilestoneUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: MilestoneStatus | None = None
    due_date: datetime | None = None


class MilestoneRead(MilestoneBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    project_id: int
    status: MilestoneStatus
    achieved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
