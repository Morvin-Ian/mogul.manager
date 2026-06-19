<div align="center">
  <h1>mogul.Manager</h1>
  <p>
    <img src="https://img.shields.io/badge/python-3.11-blue?style=flat&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/vue-3-4FC08D?style=flat&logo=vue.js" alt="Vue 3">
    <img src="https://img.shields.io/badge/postgres-17-4169E1?style=flat&logo=postgresql" alt="PostgreSQL">
    <img src="https://img.shields.io/badge/docker-compose-2496ED?style=flat&logo=docker" alt="Docker">
  </p>
</div>

---

An AI-powered project management tool where you can manage workspaces, projects, and tasks
through a chat interface. The AI agent can create, update, list, and search tasks and projects
directly from conversation — no manual form-filling needed.

---

## Features

- **Workspaces & Projects** — organize work into workspaces containing multiple projects
- **Task management** — create and track tasks with priority, status, estimated hours, and due dates
- **AI chat** — talk to the agent to take actions (e.g. "create a task for the login bug in the API project") and it will call the right tools and confirm what it did
- **Streaming responses** — agent replies stream token by token in real time

---

## Quick start with Docker

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- A [DeepSeek](https://platform.deepseek.com/) API key

### Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/Morvin-Ian/mogul.manager.git
   cd mogul.manager
   ```

2. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your own values. The defaults for `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `SECRET_KEY`,
   `S3_*`, and `FRONTEND_URL` are pre-configured for Docker — you only need to
   override them if you're using custom values.

3. **Start all services**

   ```bash
   docker compose up -d
   ```

   This starts three containers:

   | Service | Port | Description |
   |---|---|---|
   | `api` | `8000` | FastAPI backend |
   | `client` | `5173` | Vue 3 frontend (Vite dev server) |
   | `db` | `5432` | PostgreSQL 17 with pgvector |

4. **Open the app**

   Navigate to [http://localhost:5173](http://localhost:5173)

### Useful commands

```bash
# View logs
docker compose logs -f

# Follow a specific service
docker compose logs -f api

# Rebuild after dependency changes
docker compose build

# Stop everything
docker compose down

# Stop and delete database volume (⚠️ removes data)
docker compose down -v
```

---

## Running locally (without Docker)

### Backend

```bash
cp .env.example .env   # fill in DB, DeepSeek API key, S3, JWT secret
uv sync
uv run alembic upgrade head
uv run fastapi dev main.py     # starts on http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                   # starts on http://localhost:5173
```

> **Note:** Set `DATABASE_URL` in `.env` to point to your local PostgreSQL instance
> when running without Docker.
