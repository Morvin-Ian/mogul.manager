from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MemoryType = Literal["preference", "decision", "goal", "fact"]


class MemoryCreate(BaseModel):
    memory_type: MemoryType
    content: str = Field(min_length=1, max_length=1000)
    importance: int = Field(default=1, ge=1, le=3)
    source_conversation_id: int | None = None


class MemoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    memory_type: str
    content: str
    importance: int
    source_conversation_id: int | None
    created_at: datetime
    updated_at: datetime
