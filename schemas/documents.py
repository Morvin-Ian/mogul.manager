from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    title: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    summary: str | None = None
    page_count: int | None = None
    word_count: int | None = None
    chunk_count: int | None = None
    error_message: str | None = None
    url: str | None = None
    created_at: datetime
    processed_at: datetime | None = None

    model_config = {"from_attributes": True}


class ChunkResponse(BaseModel):
    id: int
    chunk_index: int
    content: str
    token_count: int

    model_config = {"from_attributes": True}


class SearchHit(BaseModel):
    document_id: int
    document_title: str
    chunk_index: int
    content: str
    similarity: float


class SearchResponse(BaseModel):
    results: list[SearchHit]
    count: int
