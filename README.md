# Mogul Manager

An AI-powered project management tool where you can manage workspaces, projects, and tasks through a chat interface. The AI agent can create, update, list, and search tasks and projects directly from conversation — no manual form-filling needed.

## What it does

- **Workspaces & Projects** — organize work into workspaces containing multiple projects
- **Task management** — create and track tasks with priority, status, estimated hours, and due dates
- **AI chat** — talk to the agent to take actions (e.g. "create a task for the login bug in the API project") and it will call the right tools and confirm what it did
- **Streaming responses** — agent replies stream token by token in real time


## Running locally

**Backend**

```bash
cp .env.example .env   # fill in DB, DeepSeek API key, S3, JWT secret
uv sync
uv run alembic upgrade head
uv run uvicorn main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```
