import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta

from fastapi import FastAPI
from sqlalchemy import select

from database import AsyncSessionLocal
from models.documents import Document, DocumentStatus
from routes.chat import comments_router
from routes.chat import router as chat_router
from routes.documents import router as documents_router
from routes.notifications import router as notifications_router
from routes.project import plans_router, tasks_router
from routes.project import router as projects_router
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
    """Requeue documents stuck in pending/processing for longer than the staleness threshold."""
    cutoff = datetime.now(UTC) - timedelta(seconds=_STUCK_THRESHOLD_SECONDS)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Document.id).where(
                Document.status.in_(
                    [DocumentStatus.pending, DocumentStatus.processing]
                ),
                Document.updated_at < cutoff,
            )
        )
        doc_ids = [row[0] for row in result.fetchall()]

    if doc_ids:
        logger.info(
            "Requeueing %d stuck document(s) (older than %ds)",
            len(doc_ids),
            _STUCK_THRESHOLD_SECONDS,
        )
        for doc_id in doc_ids:
            asyncio.create_task(process_document_bg(doc_id))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await warmup_embeddings()
    await _requeue_pending_documents()
    periodic_task = asyncio.create_task(_periodic_document_check())
    yield
    periodic_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await periodic_task


app = FastAPI(lifespan=lifespan)

app.include_router(users_router)
app.include_router(google_router)
app.include_router(workspaces_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(plans_router)
app.include_router(chat_router)
app.include_router(comments_router)
app.include_router(documents_router)
app.include_router(members_router)
app.include_router(invitations_router)
app.include_router(notifications_router)
