from __future__ import annotations

import logging
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import boto3
from fastapi import Depends
from openai import AsyncOpenAI
from sqlalchemy import delete as sa_delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from config import settings
from database import AsyncSessionLocal, get_db
from models.documents import Document, DocumentChunk, DocumentStatus, DocumentType
from services.chunker import chunk_text
from services.embeddings import embed_texts
from services.text_extractor import extract_text

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS: dict[str, DocumentType] = {
    ".pdf": DocumentType.pdf,
    ".docx": DocumentType.docx,
    ".txt": DocumentType.txt,
    ".csv": DocumentType.csv,
}

ALLOWED_CONTENT_TYPES: dict[str, DocumentType] = {
    "application/pdf": DocumentType.pdf,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocumentType.docx,
    "text/plain": DocumentType.txt,
    "text/csv": DocumentType.csv,
    "application/csv": DocumentType.csv,
}

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
SUMMARY_PREVIEW_CHARS = 4000


class DocumentService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def list_documents(self, user_id: int) -> list[Document]:
        result = await self.db.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_document(self, document_id: int, user_id: int) -> Document | None:
        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id, Document.user_id == user_id
            )
        )
        return result.scalars().first()

    async def delete_document(self, document_id: int, user_id: int) -> bool:
        doc = await self.get_document(document_id, user_id)
        if not doc:
            return False
        if doc.storage_key:
            try:
                await run_in_threadpool(_s3_delete, doc.storage_key)
            except Exception as e:
                logger.warning("S3 delete failed for %s: %s", doc.storage_key, e)
        await self.db.delete(doc)
        await self.db.commit()
        return True

    # ── Upload ─────────────────────────────────────────────────────────────────

    async def create_from_upload(
        self,
        user_id: int,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> Document:
        ext = Path(filename).suffix.lower()
        file_type = ALLOWED_EXTENSIONS.get(ext) or ALLOWED_CONTENT_TYPES.get(
            content_type
        )
        if not file_type:
            raise ValueError("Unsupported file type. Allowed: PDF, DOCX, TXT, CSV")
        if len(content) > MAX_FILE_SIZE:
            raise ValueError("File exceeds the 20 MB size limit.")

        storage_key = f"documents/{uuid.uuid4().hex}{ext}"
        await run_in_threadpool(_s3_upload, content, storage_key)

        doc = Document(
            user_id=user_id,
            title=filename,
            original_filename=filename,
            file_type=file_type,
            file_size=len(content),
            storage_key=storage_key,
            status=DocumentStatus.pending,
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def process(self, document_id: int) -> None:
        """Full pipeline in the current DB session (call only when session is open)."""
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        doc = result.scalars().first()
        if not doc:
            return
        await _run_pipeline(self.db, doc)


async def process_document_bg(document_id: int) -> None:
    """Creates its own session — safe to call from BackgroundTasks."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Document).where(Document.id == document_id))
        doc = result.scalars().first()
        if doc:
            await _run_pipeline(db, doc)


async def _run_pipeline(db: AsyncSession, doc: Document) -> None:
    t0 = time.perf_counter()
    logger.info("[doc=%s] Pipeline start — %s", doc.id, doc.original_filename)
    doc.status = DocumentStatus.processing
    await db.commit()

    try:
        if not doc.storage_key:
            raise ValueError("Document has no storage key.")

        t = time.perf_counter()
        content = await run_in_threadpool(_s3_download, doc.storage_key)
        logger.info("[doc=%s] S3 download %.2fs", doc.id, time.perf_counter() - t)

        t = time.perf_counter()
        text, meta = await extract_text(content, doc.file_type.value)
        logger.info(
            "[doc=%s] Text extraction %.2fs — %s words, %s pages",
            doc.id, time.perf_counter() - t, meta.get("word_count"), meta.get("page_count"),
        )

        if not text.strip():
            raise ValueError("No text could be extracted from this document.")

        doc.word_count = meta.get("word_count")
        doc.page_count = meta.get("page_count")

        t = time.perf_counter()
        chunks = chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        doc.chunk_count = len(chunks)
        logger.info("[doc=%s] Chunked into %s chunks %.3fs", doc.id, doc.chunk_count, time.perf_counter() - t)

        t = time.perf_counter()
        all_embeddings = await embed_texts(chunks)
        logger.info("[doc=%s] Embedded %s chunks %.2fs", doc.id, len(chunks), time.perf_counter() - t)

        t = time.perf_counter()
        await db.execute(sa_delete(DocumentChunk).where(DocumentChunk.document_id == doc.id))
        await db.execute(
            insert(DocumentChunk),
            [
                {
                    "document_id": doc.id,
                    "chunk_index": idx,
                    "content": chunk,
                    "token_count": len(chunk.split()),
                    "embedding": emb,
                }
                for idx, (chunk, emb) in enumerate(zip(chunks, all_embeddings))
            ],
        )
        logger.info("[doc=%s] Persisted %s chunks %.2fs", doc.id, len(chunks), time.perf_counter() - t)

        t = time.perf_counter()
        doc.summary = await _generate_summary(text[:SUMMARY_PREVIEW_CHARS], doc.title)
        logger.info("[doc=%s] Summary generated %.2fs", doc.id, time.perf_counter() - t)

        doc.status = DocumentStatus.ready
        doc.processed_at = datetime.now(UTC)
        logger.info("[doc=%s] Pipeline complete in %.2fs", doc.id, time.perf_counter() - t0)

    except Exception as exc:
        logger.error("[doc=%s] Pipeline failed: %s", doc.id, exc, exc_info=True)
        doc.status = DocumentStatus.failed
        doc.error_message = str(exc)

    await db.commit()


async def _generate_summary(text_preview: str, title: str) -> str:
    try:
        client = AsyncOpenAI(
            api_key=settings.deepseek_api_key.get_secret_value(),
            base_url=settings.deepseek_base_url,
        )
        resp = await client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a document analyst. Write a concise 3-5 sentence summary "
                        "covering the main topic, key points, and any actionable takeaways."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Document: {title}\n\n{text_preview}",
                },
            ],
            max_tokens=300,
            stream=False,
        )
        return resp.choices[0].message.content or ""
    except Exception as exc:
        logger.warning("Summary generation failed: %s", exc)
        return ""


def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key_id.get_secret_value(),
        aws_secret_access_key=settings.s3_secret_access_key.get_secret_value(),
    )


def _s3_upload(content: bytes, key: str) -> None:
    _s3_client().put_object(Bucket=settings.s3_bucket_name, Key=key, Body=content)


def _s3_download(key: str) -> bytes:
    resp = _s3_client().get_object(Bucket=settings.s3_bucket_name, Key=key)
    return resp["Body"].read()


def _s3_delete(key: str) -> None:
    _s3_client().delete_object(Bucket=settings.s3_bucket_name, Key=key)
