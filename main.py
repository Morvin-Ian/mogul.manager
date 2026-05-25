import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from routes import memory, plans
from routes.chat import router as chat_router, comments_router
from routes.documents import router as documents_router
from routes.project import router as projects_router, tasks_router
from routes.user import router as users_router, google_router
from routes.workspace import router as workspaces_router, members_router, invitations_router
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
app.include_router(workspaces_router)
app.include_router(projects_router)
app.include_router(tasks_router)
app.include_router(chat_router)
app.include_router(comments_router)
app.include_router(memory.router)
app.include_router(plans.router)
app.include_router(documents_router)
app.include_router(members_router)
app.include_router(invitations_router)
app.include_router(google_router)
