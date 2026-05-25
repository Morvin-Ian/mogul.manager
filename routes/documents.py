from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.documents import DocumentResponse, SearchResponse, SearchHit
from services.auth import CurrentUser
from services.documents import (
    ALLOWED_CONTENT_TYPES,
    ALLOWED_EXTENSIONS,
    DocumentService,
    process_document_bg,
)
from services.rag import RAGService
from pathlib import Path

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    return await DocumentService(db).list_documents(current_user.id)


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
):
    filename = file.filename or "document"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS and (file.content_type or "") not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(400, "Unsupported file type. Allowed: PDF, DOCX, TXT, CSV")

    content = await file.read()

    try:
        doc = await DocumentService(db).create_from_upload(
            user_id=current_user.id,
            filename=filename,
            content=content,
            content_type=file.content_type or "",
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc))

    background_tasks.add_task(process_document_bg, doc.id)
    return doc


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    doc = await DocumentService(db).get_document(document_id, current_user.id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    ok = await DocumentService(db).delete_document(document_id, current_user.id)
    if not ok:
        raise HTTPException(404, "Document not found")


@router.post("/{document_id}/reprocess", response_model=DocumentResponse)
async def reprocess_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    doc = await DocumentService(db).get_document(document_id, current_user.id)
    if not doc:
        raise HTTPException(404, "Document not found")
    background_tasks.add_task(process_document_bg, doc.id)
    return doc


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    body: dict,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    query = body.get("query", "").strip()
    if not query:
        raise HTTPException(400, "query is required")
    top_k = min(int(body.get("top_k", 5)), 20)

    hits = await RAGService(db).search(query, current_user.id, top_k=top_k)
    return SearchResponse(
        results=[SearchHit(**h) for h in hits],
        count=len(hits),
    )
