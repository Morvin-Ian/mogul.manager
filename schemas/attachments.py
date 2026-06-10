from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttachmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    task_id: int
    user_id: int
    original_filename: str
    file_size: int
    mime_type: str
    url: str
    uploader_name: str | None = None
    created_at: datetime


class AttachmentList(BaseModel):
    items: list[AttachmentRead]
    total: int
