import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routes import chat, comments, memory, plans, projects, tasks, users, workspaces

os.makedirs("static", exist_ok=True)
os.makedirs("media", exist_ok=True)


app = FastAPI()

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
