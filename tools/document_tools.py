import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from services.documents import DocumentService
from services.documents.rag import RAGService

DOCUMENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_documents",
            "description": "List all documents the user has uploaded.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "The current user's ID"},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": (
                "Semantically search through the user's uploaded documents to find relevant "
                "information. Use this to answer questions based on uploaded files, extract "
                "insights, or find specific information across multiple documents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question or topic to search for in the documents",
                    },
                    "user_id": {"type": "integer"},
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default 5)",
                        "default": 5,
                    },
                },
                "required": ["query", "user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_document_summary",
            "description": "Get the AI-generated summary and metadata for a specific document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {"type": "integer"},
                    "user_id": {"type": "integer"},
                },
                "required": ["document_id", "user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "answer_from_documents",
            "description": (
                "Answer a specific question by searching the user's documents and synthesising "
                "an answer from the most relevant excerpts. Ideal for Q&A over uploaded files."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "user_id": {"type": "integer"},
                },
                "required": ["question", "user_id"],
            },
        },
    },
]


async def handle(name: str, args: dict[str, Any], db: AsyncSession) -> str:
    svc = DocumentService(db)
    rag = RAGService(db)

    if name == "list_documents":
        docs = await svc.list_documents(args["user_id"])
        return json.dumps(
            [
                {
                    "id": d.id,
                    "title": d.title,
                    "file_type": d.file_type.value,
                    "status": d.status.value,
                    "word_count": d.word_count,
                    "chunk_count": d.chunk_count,
                    "summary": (d.summary or "")[:300],
                    "created_at": d.created_at.isoformat(),
                }
                for d in docs
            ]
        )

    if name == "search_documents":
        hits = await rag.search(
            query=args["query"],
            user_id=args["user_id"],
            top_k=args.get("top_k", 5),
        )
        return json.dumps({"results": hits, "count": len(hits)})

    if name == "get_document_summary":
        doc = await svc.get_document(args["document_id"], args["user_id"])
        if not doc:
            return json.dumps({"error": "Document not found"})
        return json.dumps(
            {
                "id": doc.id,
                "title": doc.title,
                "status": doc.status.value,
                "summary": doc.summary,
                "word_count": doc.word_count,
                "page_count": doc.page_count,
                "chunk_count": doc.chunk_count,
                "url": doc.url,
            }
        )

    if name == "answer_from_documents":
        hits = await rag.search(
            query=args["question"],
            user_id=args["user_id"],
            top_k=6,
        )
        if not hits:
            return json.dumps({"answer": "No relevant documents found.", "sources": []})

        context = "\n\n".join(
            f'[{h["document_title"]}]: {h["content"]}' for h in hits
        )
        sources = list({h["document_title"] for h in hits})
        return json.dumps({"context": context, "sources": sources})

    return json.dumps({"error": f"Unknown tool: {name}"})
