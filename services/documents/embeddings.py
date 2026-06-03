from __future__ import annotations

import logging

import numpy as np
from fastembed import TextEmbedding  # type: ignore[import]
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 384
_MODEL_NAME = "BAAI/bge-small-en-v1.5"
_model: TextEmbedding | None = None

# Max texts sent to ONNX in one call — keeps RAM flat regardless of doc size.
_EMBED_BATCH_SIZE = 64


def _get_model() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=_MODEL_NAME)
        logger.info("Embedding model loaded: %s", _MODEL_NAME)
    return _model


def _embed_sync(texts: list[str]) -> list[np.ndarray]:
    model = _get_model()
    results: list[np.ndarray] = []
    for i in range(0, len(texts), _EMBED_BATCH_SIZE):
        batch = texts[i : i + _EMBED_BATCH_SIZE]
        results.extend(model.embed(batch))
    return results


async def warmup() -> None:
    """Load and warm the ONNX model in a background thread at startup."""
    await run_in_threadpool(_get_model)
    logger.info("Embedding model ready: %s", _MODEL_NAME)


async def embed_texts(texts: list[str]) -> list[np.ndarray]:
    """Generate embeddings for a batch of texts, returned as numpy float32 arrays."""
    return await run_in_threadpool(_embed_sync, texts)


async def embed_text(text: str) -> np.ndarray:
    """Generate embedding for a single text."""
    results = await embed_texts([text])
    return results[0]
