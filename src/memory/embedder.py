"""
Embedding generation for vector memory.
Uses sentence-transformers with lazy loading and singleton pattern.
"""

from __future__ import annotations
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy-loaded singleton
_embedder: Optional["_EmbedderWrapper"] = None


class _EmbedderWrapper:
    """Wraps sentence-transformers with lazy init.

    The model (~80MB) is only loaded on first use, not at import time.
    This ensures --no-memory flows are not affected.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            logger.info("Loading embedding model: %s", self._model_name)
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
            logger.info("Embedding model loaded.")
        return self._model

    def encode(self, text: str) -> list[float]:
        """Generate embedding vector for a text string.

        Returns a normalized 384-dimensional vector.
        Normalization ensures cosine similarity = dot product.
        """
        return self.model.encode(text, normalize_embeddings=True).tolist()


def get_embedder(model_name: str = "all-MiniLM-L6-v2") -> _EmbedderWrapper:
    """Get or create the singleton embedder instance."""
    global _embedder
    if _embedder is None:
        _embedder = _EmbedderWrapper(model_name)
    return _embedder


def embed_diff(diff: str) -> list[float]:
    """Generate embedding for a git diff string.

    Strategy: Use the first 2000 chars of the diff as the embedding source.
    This captures the overall nature of the change (file paths, change types)
    without wasting compute on very large diffs. Also appends the last 500
    chars to capture the tail of the diff.
    """
    head = diff[:2000]
    tail = diff[-500:] if len(diff) > 2500 else ""

    text = head + ("\n...\n" + tail if tail else "")
    return get_embedder().encode(text)


def embed_text(text: str) -> list[float]:
    """Generate embedding for arbitrary text (max 2000 chars)."""
    return get_embedder().encode(text[:2000])
