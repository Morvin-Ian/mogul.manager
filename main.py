import asyncio
import contextlib
import hashlib
import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from time import monotonic

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import or_, select

from config import settings
from database import AsyncSessionLocal
from models.documents import Document, DocumentStatus
from routes.activity import router as activity_router
from routes.attachments import router as attachments_router
from routes.chat import comments_router
from routes.chat import router as chat_router
from routes.dependencies import router as dependencies_router
from routes.documents import router as documents_router
from routes.notifications import router as notifications_router
from routes.project import milestones_router, plans_router, tags_router, tasks_router
from routes.project import router as projects_router
from routes.reports import router as reports_router
from routes.user import google_router
from routes.user import router as users_router
from routes.workspace import invitations_router, members_router
from routes.workspace import router as workspaces_router
from services.documents.embeddings import warmup as warmup_embeddings
from services.documents.service import process_document_bg

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


# A document must be stuck in pending/processing for this long before we retry it.
# Prevents race-condition double-processing of docs that just started.
_STUCK_THRESHOLD_SECONDS = 900  # 15 minutes
_MAX_PROCESSING_ATTEMPTS = 3


async def _periodic_document_check(interval_seconds: int = 1800) -> None:
    """Every 30 minutes requeue documents that are genuinely stuck."""
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            await _requeue_pending_documents()
        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.error("Periodic document check error: %s", exc)


async def _requeue_pending_documents() -> None:
    """Requeue stuck (pending/processing) and retryable failed documents."""
    cutoff = datetime.now(UTC) - timedelta(seconds=_STUCK_THRESHOLD_SECONDS)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Document.id).where(
                or_(
                    Document.status.in_(
                        [DocumentStatus.pending, DocumentStatus.processing]
                    ),
                    # Transient failures get a bounded number of retries
                    (Document.status == DocumentStatus.failed)
                    & (Document.processing_attempts < _MAX_PROCESSING_ATTEMPTS),
                ),
                Document.updated_at < cutoff,
            )
        )
        doc_ids = [row[0] for row in result.fetchall()]

    if doc_ids:
        logger.info(
            "Requeueing %d stuck/failed document(s) (older than %ds)",
            len(doc_ids),
            _STUCK_THRESHOLD_SECONDS,
        )
        for doc_id in doc_ids:
            asyncio.create_task(process_document_bg(doc_id))


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.refresh_secret_key is None:
        logger.warning(
            "REFRESH_SECRET_KEY is not set — falling back to SECRET_KEY for "
            "refresh tokens. Set a separate secret in production."
        )
    try:
        await warmup_embeddings()
    except Exception:
        logger.warning(
            "Embedding model not available — will load on demand", exc_info=True
        )
    await _requeue_pending_documents()
    periodic_task = asyncio.create_task(_periodic_document_check())
    yield
    periodic_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await periodic_task


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url.rstrip("/")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Write rate limiting ─────────────────────────────────────────────
# In-memory sliding window per caller (Authorization header hash, else IP).
# Generous ceiling — meant to stop abuse/runaway scripts, not real usage.
# Note: per-process only; use a shared store (e.g. Redis) if scaled out.
_WRITE_METHODS = {"POST", "PATCH", "PUT", "DELETE"}
_WRITE_RATE_WINDOW = 60.0
_WRITE_RATE_MAX = 240
_write_timestamps: dict[str, list[float]] = {}


@app.middleware("http")
async def write_rate_limit(request: Request, call_next):
    if request.method in _WRITE_METHODS and request.url.path.startswith("/api"):
        auth_header = request.headers.get("authorization")
        if auth_header:
            key = hashlib.sha256(auth_header.encode()).hexdigest()[:16]
        else:
            key = request.client.host if request.client else "unknown"
        now = monotonic()
        ts = [t for t in _write_timestamps.get(key, []) if now - t < _WRITE_RATE_WINDOW]
        if len(ts) >= _WRITE_RATE_MAX:
            _write_timestamps[key] = ts
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
            )
        ts.append(now)
        _write_timestamps[key] = ts
    return await call_next(request)


@app.get("/health")
async def healthcheck():
    """Liveness/readiness probe — verifies the DB connection."""
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(select(1))
    except Exception:
        return JSONResponse(
            status_code=503, content={"status": "degraded", "database": "unreachable"}
        )
    return {"status": "ok"}


app.include_router(users_router)
app.include_router(google_router)
app.include_router(workspaces_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(plans_router)
app.include_router(tags_router)
app.include_router(milestones_router)
app.include_router(chat_router)
app.include_router(dependencies_router)
app.include_router(comments_router)
app.include_router(documents_router)
app.include_router(members_router)
app.include_router(invitations_router)
app.include_router(notifications_router)
app.include_router(activity_router)
app.include_router(attachments_router)
app.include_router(reports_router)
