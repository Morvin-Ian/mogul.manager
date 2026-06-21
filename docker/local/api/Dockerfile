FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV FASTEMBED_CACHE_DIR=/opt/fastembed_cache
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH=/opt/venv/bin:$PATH

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Pre-download the embedding model so it's baked into the image
RUN uv run python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='BAAI/bge-small-en-v1.5')"

COPY docker/local/api/start /start
COPY . .

EXPOSE 8000
