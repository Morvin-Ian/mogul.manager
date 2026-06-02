import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from routes.chat import comments_router
from routes.chat import router as chat_router
from routes.documents import router as documents_router
from routes.project import router as projects_router
from routes.project import tasks_router
from routes.user import google_router
from routes.user import router as users_router
from routes.workspace import invitations_router, members_router
from routes.workspace import router as workspaces_router
from services.documents.embeddings import warmup as warmup_embeddings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await warmup_embeddings()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router)
app.include_router(google_router)
app.include_router(workspaces_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(chat_router)
app.include_router(comments_router)
app.include_router(documents_router)
app.include_router(members_router)
app.include_router(invitations_router)
app.include_router(google_router)
