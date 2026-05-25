import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routes import chat, comments, documents, memory, plans, projects, tasks, users, workspaces
from services.embeddings import warmup as warmup_embeddings

os.makedirs("static", exist_ok=True)
os.makedirs("media", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await warmup_embeddings()
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")

app.include_router(users.router)
app.include_router(workspaces.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(chat.router)
app.include_router(comments.router)
app.include_router(memory.router)
app.include_router(plans.router)
app.include_router(documents.router)
