import logging
from datetime import UTC, datetime
from pathlib import Path

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool as _rtp

import models
from config import settings
from database import get_db
from models.collaboration import MemberRole, WorkspaceMember
from models.documents import DocumentChunk, DocumentStatus
from schemas.documents import (
    DocumentResponse,
    DocumentUpdate,
    SearchHit,
    SearchResponse,
)
from services.auth import CurrentUser
from services.documents import (
    ALLOWED_CONTENT_TYPES,
    ALLOWED_EXTENSIONS,
    DocumentService,
    process_document_bg,
)
from services.documents.rag import RAGService
from services.documents.service import _s3_client, _s3_download

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    project_id: int | None = Query(None),
    workspace_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    svc = DocumentService(db)
    if project_id is not None:
        return await svc.list_by_project(project_id, current_user.id, skip=skip, limit=limit)
    if workspace_id is not None:
        return await svc.list_by_workspace(workspace_id, current_user.id, skip=skip, limit=limit)
    return await svc.list_documents(current_user.id, skip=skip, limit=limit)


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    current_user: CurrentUser,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    project_id: int | None = Form(None),
):
    filename = file.filename or "document"
    ext = Path(filename).suffix.lower()
    if (
        ext not in ALLOWED_EXTENSIONS
        and (file.content_type or "") not in ALLOWED_CONTENT_TYPES
    ):
        raise HTTPException(400, "Unsupported file type. Allowed: PDF, DOCX, TXT, CSV")

    content = await file.read()

    try:
        doc = await DocumentService(db).create_from_upload(
            user_id=current_user.id,
            filename=filename,
            content=content,
            content_type=file.content_type or "",
            project_id=project_id,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except (BotoCoreError, ClientError) as exc:
        logger.error("Document upload to storage failed: %s", exc)
        raise HTTPException(503, "File storage is temporarily unavailable. Please try again.")

    background_tasks.add_task(process_document_bg, doc.id)
    return doc


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    doc = await DocumentService(db).get_by_uuid(document_id, current_user.id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    svc = DocumentService(db)
    doc_obj = await svc.get_by_uuid_any(document_id)
    if not doc_obj:
        raise HTTPException(404, "Document not found")
    if doc_obj.user_id != current_user.id:
        raise HTTPException(403, "You don't have permission to delete this document")
    ok = await svc.delete_document(doc_obj.id, current_user.id)
    if not ok:
        raise HTTPException(404, "Document not found")


_REPROCESS_COOLDOWN_SECONDS = 120


@router.post("/{document_id}/reprocess", response_model=DocumentResponse)
async def reprocess_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    svc = DocumentService(db)
    doc = await svc.get_by_uuid(document_id, current_user.id)
    if not doc:
        raise HTTPException(404, "Document not found")
    if doc.status in (DocumentStatus.pending, DocumentStatus.processing):
        raise HTTPException(429, "Document is already queued for processing")
    age = (datetime.now(UTC) - doc.updated_at).total_seconds()
    if age < _REPROCESS_COOLDOWN_SECONDS:
        raise HTTPException(
            429,
            f"Document was processed moments ago — try again in {int(_REPROCESS_COOLDOWN_SECONDS - age)}s",
        )
    background_tasks.add_task(process_document_bg, doc.id)
    return doc


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    body: DocumentUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Reassign a document to a different project (or make it general)."""
    svc = DocumentService(db)
    doc = await svc.get_by_uuid_any(document_id)
    if not doc:
        raise HTTPException(404, "Document not found")

    # Rights check: uploader can always reassign; others need admin/owner role
    if doc.user_id != current_user.id:
        check_project_id = doc.project_id or body.project_id
        if not check_project_id:
            raise HTTPException(403, "Only the document owner can modify this document")
        proj_result = await db.execute(
            select(models.Project).where(models.Project.id == check_project_id)
        )
        project = proj_result.scalars().first()
        if not project:
            raise HTTPException(404, "Project not found")
        member_result = await db.execute(
            select(WorkspaceMember).where(
                WorkspaceMember.workspace_id == project.workspace_id,
                WorkspaceMember.user_id == current_user.id,
            )
        )
        member = member_result.scalars().first()
        if not member or member.role not in (MemberRole.admin, MemberRole.owner):
            raise HTTPException(
                403, "Admin or owner role required to reassign this document"
            )

    doc.project_id = body.project_id
    await db.commit()
    await db.refresh(doc)
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


@router.get("/{document_id}/file")
async def stream_document_file(
    document_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Proxy the raw file from S3 with inline Content-Disposition for in-browser viewing."""
    _MIME = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain; charset=utf-8",
        "csv": "text/csv; charset=utf-8",
    }

    doc = await DocumentService(db).get_by_uuid(document_id, current_user.id)
    if not doc:
        raise HTTPException(404, "Document not found")
    if not doc.storage_key:
        raise HTTPException(404, "File not stored")

    storage_key = doc.storage_key
    content = await _rtp(lambda: _s3_download(storage_key))
    media_type = _MIME.get(doc.file_type.value, "application/octet-stream")

    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'inline; filename="{doc.original_filename}"',
            "Content-Length": str(len(content)),
            "Cache-Control": "private, max-age=3600",
        },
    )


@router.get("/{document_id}/view-url")
async def get_view_url(
    document_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return a short-lived presigned URL for in-browser viewing."""
    doc = await DocumentService(db).get_by_uuid(document_id, current_user.id)
    if not doc:
        raise HTTPException(404, "Document not found")
    if not doc.storage_key:
        raise HTTPException(404, "File not available")

    storage_key = doc.storage_key
    url = await _rtp(
        lambda: _s3_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket_name, "Key": storage_key},
            ExpiresIn=3600,
        )
    )
    return {
        "url": url,
        "file_type": doc.file_type.value,
        "filename": doc.original_filename,
    }


@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Return all text chunks for a document (used by the in-app text viewer)."""
    doc = await DocumentService(db).get_by_uuid(document_id, current_user.id)
    if not doc:
        raise HTTPException(404, "Document not found")

    result = await db.execute(
        select(DocumentChunk.chunk_index, DocumentChunk.content)
        .where(DocumentChunk.document_id == doc.id)
        .order_by(DocumentChunk.chunk_index)
    )
    return [{"index": r.chunk_index, "content": r.content} for r in result.all()]
