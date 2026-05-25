from __future__ import annotations

import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.documents import Document, DocumentChunk, DocumentStatus
from services.documents.embeddings import embed_text

logger = logging.getLogger(__name__)

TOP_K_DEFAULT = 5
MIN_SIMILARITY = 0.30  # cosine similarity threshold (0–1)


class RAGService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def search(
        self,
        query: str,
        user_id: int,
        top_k: int = TOP_K_DEFAULT,
        min_similarity: float = MIN_SIMILARITY,
    ) -> list[dict]:
        """Return ranked list of matching chunks with similarity scores."""
        try:
            query_embedding = await embed_text(query)
        except Exception as exc:
            logger.warning("Embedding failed for RAG query: %s", exc)
            return []

        distance_col = DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")

        result = await self.db.execute(
            select(DocumentChunk, Document.title.label("doc_title"), distance_col)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.user_id == user_id)
            .where(Document.status == DocumentStatus.ready)
            .where(DocumentChunk.embedding.is_not(None))
            .order_by(distance_col)
            .limit(top_k)
        )

        hits: list[dict] = []
        for chunk, doc_title, distance in result.all():
            similarity = round(1.0 - float(distance), 3)
            if similarity >= min_similarity:
                hits.append(
                    {
                        "document_id": chunk.document_id,
                        "document_title": doc_title,
                        "chunk_index": chunk.chunk_index,
                        "content": chunk.content,
                        "similarity": similarity,
                    }
                )
        return hits

    async def build_rag_context(self, query: str, user_id: int) -> str:
        """Build a formatted context string to prepend to the AI's system prompt."""
        hits = await self.search(query, user_id, top_k=4)
        if not hits:
            return ""

        lines = ["[Relevant excerpts from your documents]"]
        seen: set[int] = set()
        for hit in hits:
            if hit["document_id"] not in seen:
                lines.append(f'\nFrom "{hit["document_title"]}":')
                seen.add(hit["document_id"])
            lines.append(f'  • {hit["content"]}')
        lines.append("[End of excerpts]")
        return "\n".join(lines)
