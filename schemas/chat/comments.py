from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentBase(BaseModel):
    content: str = Field(min_length=1)


class CommentCreate(CommentBase):
    task_id: int


class CommentUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1)


class CommentRead(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    task_id: int
    created_at: datetime
    updated_at: datetime
