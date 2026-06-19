from __future__ import annotations

import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.collaboration import WorkspaceMember
from models.documents import Document, DocumentChunk, DocumentStatus
from models.projects import Project
from services.documents.embeddings import embed_text

logger = logging.getLogger(__name__)

TOP_K_DEFAULT = 5
MIN_SIMILARITY = 0.30
_HYBRID_VECTOR_MULTIPLIER = 3
_HYBRID_KEYWORD_K = 10
_RERANK_CANDIDATES = 20

_reranker: object = None


def _get_reranker():
    global _reranker
    if _reranker is not None:
        return _reranker
    try:
        from fastembed import Reranker as _RerankerCls

        _reranker = _RerankerCls(
            model_name="Xenova/ms-marco-MiniLM-L-6-v2",
            providers=None,
        )
        logger.info("Cross-encoder reranker loaded")
    except Exception as exc:
        logger.info(
            "Cross-encoder reranker not available (falls back to score-only): %s", exc
        )
        _reranker = False
    return _reranker


class RAGService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def _accessible_doc_ids(
        self, user_id: int, workspace_id: int | None = None
    ) -> set[int]:
        accessible_project_ids = (
            select(Project.id)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Project.workspace_id)
            .where(WorkspaceMember.user_id == user_id)
        )
        if workspace_id is not None:
            accessible_project_ids = accessible_project_ids.where(
                Project.workspace_id == workspace_id
            )
        result = await self.db.execute(
            select(Document.id).where(
                or_(
                    Document.user_id == user_id,
                    Document.project_id.in_(accessible_project_ids),
                ),
                Document.status == DocumentStatus.ready,
            )
        )
        return {row[0] for row in result.all()}

    async def search(
        self,
        query: str,
        user_id: int,
        top_k: int = TOP_K_DEFAULT,
        min_similarity: float = MIN_SIMILARITY,
        workspace_id: int | None = None,
    ) -> list[dict]:
        doc_ids = await self._accessible_doc_ids(user_id, workspace_id)
        if not doc_ids:
            return []

        try:
            query_embedding = await embed_text(query)
        except Exception as exc:
            logger.warning("Embedding failed for RAG query: %s", exc)
            return []

        distance_col = DocumentChunk.embedding.cosine_distance(query_embedding).label(
            "distance"
        )

        vector_results = await self.db.execute(
            select(DocumentChunk, Document.title.label("doc_title"), distance_col)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(DocumentChunk.document_id.in_(doc_ids))
            .where(DocumentChunk.embedding.is_not(None))
            .order_by(distance_col)
            .limit(top_k * _HYBRID_VECTOR_MULTIPLIER)
        )

        hits_map: dict[int, dict] = {}
        for chunk, doc_title, distance in vector_results.all():
            similarity = round(1.0 - float(distance), 3)
            if similarity >= min_similarity:
                hits_map[chunk.id] = {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_title": doc_title,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "similarity": similarity,
                    "keyword_score": 0.0,
                }

        keyword_pattern = f"%{query}%"
        kw_results = await self.db.execute(
            select(DocumentChunk, Document.title.label("doc_title"))
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(DocumentChunk.document_id.in_(doc_ids))
            .where(
                or_(
                    DocumentChunk.content.ilike(keyword_pattern),
                    Document.title.ilike(keyword_pattern),
                )
            )
            .limit(_HYBRID_KEYWORD_K)
        )

        for chunk, doc_title in kw_results.all():
            if chunk.id in hits_map:
                hits_map[chunk.id]["keyword_score"] = 1.0
            else:
                hits_map[chunk.id] = {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_title": doc_title,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "similarity": 0.0,
                    "keyword_score": 1.0,
                }

        if not hits_map:
            return []

        hits = list(hits_map.values())
        for h in hits:
            h["combined_score"] = h["similarity"] * 0.7 + h["keyword_score"] * 0.3

        hits.sort(key=lambda h: h["combined_score"], reverse=True)
        candidates = hits[:_RERANK_CANDIDATES]

        reranker = _get_reranker()
        if reranker:
            try:
                pairs = [(query, h["content"]) for h in candidates]
                scores = list(reranker.rerank(pairs))
                for h, score in zip(candidates, scores):
                    h["rerank_score"] = round(float(score), 4)
                    h["combined_score"] = h["rerank_score"]
                candidates.sort(key=lambda h: h["rerank_score"], reverse=True)
            except Exception as exc:
                logger.warning("Reranker failed, using combined scores: %s", exc)

        return candidates[:top_k]

    async def search_keyword(
        self,
        query: str,
        user_id: int,
        top_k: int = TOP_K_DEFAULT,
        workspace_id: int | None = None,
    ) -> list[dict]:
        doc_ids = await self._accessible_doc_ids(user_id, workspace_id)
        if not doc_ids:
            return []

        pattern = f"%{query}%"
        result = await self.db.execute(
            select(DocumentChunk, Document.title.label("doc_title"))
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(DocumentChunk.document_id.in_(doc_ids))
            .where(
                or_(
                    DocumentChunk.content.ilike(pattern),
                    Document.title.ilike(pattern),
                )
            )
            .order_by(DocumentChunk.document_id, DocumentChunk.chunk_index)
            .limit(top_k)
        )
        return [
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "document_title": doc_title,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "similarity": 1.0,
            }
            for chunk, doc_title in result.all()
        ]

    async def build_rag_context(
        self,
        query: str,
        user_id: int,
        workspace_id: int | None = None,
    ) -> str:
        hits = await self.search(query, user_id, top_k=4, workspace_id=workspace_id)
        if not hits:
            return ""

        lines = ["[Relevant excerpts from your documents]"]
        seen: set[int] = set()
        for hit in hits:
            if hit["document_id"] not in seen:
                lines.append(f'\nFrom "{hit["document_title"]}":')
                seen.add(hit["document_id"])
            lines.append(f"  • {hit['content']}")
        lines.append("[End of excerpts]")
        return "\n".join(lines)
