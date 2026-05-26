from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    profile_path: str | None = None


class CommentBase(BaseModel):
    content: str = Field(min_length=1)


class CommentCreate(CommentBase):
    task_id: int
    parent_id: int | None = None


class CommentUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1)


class CommentRead(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    task_id: int
    parent_id: int | None = None
    user: UserBrief | None = None
    created_at: datetime
    updated_at: datetime
