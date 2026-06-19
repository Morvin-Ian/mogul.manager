<div align="center">
  <h1>mogul.Manager</h1>
  <p>
    <img src="https://img.shields.io/badge/python-3.11-blue?style=flat&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/vue-3-4FC08D?style=flat&logo=vue.js" alt="Vue 3">
    <img src="https://img.shields.io/badge/postgres-17-4169E1?style=flat&logo=postgresql" alt="PostgreSQL">
    <img src="https://img.shields.io/badge/docker-compose-2496ED?style=flat&logo=docker" alt="Docker">
  </p>
</div>

AI-powered project management with a chat interface.

## Docker

```bash
cp .env.example .env
docker compose up -d
```

Open [http://localhost:5173](http://localhost:5173)

## Local

**Backend**
```bash
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run fastapi dev main.py
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```
