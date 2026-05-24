"""
Vector Memory module — lưu lịch sử review và retrieve các review tương tự.

Usage:
    from src.memory import get_memory_store

    store = get_memory_store(db_path=".roo/memory/vector_db", project="my-project")
    similar = store.query_similar(query)
    store.add_review(record)
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional

from src.memory.store import VectorMemoryStore
from src.memory.models import ReviewRecord, MemoryQuery, MemoryResult
from src.memory.embedder import embed_diff, embed_text, get_embedder

# Module-level cache for store instances (one per project)
_instances: dict[str, VectorMemoryStore] = {}


def get_memory_store(
    db_path: str | Path = ".roo/memory/vector_db",
    project: str = "default",
) -> Optional[VectorMemoryStore]:
    """Get or create a VectorMemoryStore for the given project.

    Returns None if chromadb is not installed (graceful degradation).
    """
    try:
        import chromadb  # noqa: F401 — verify import works
    except ImportError:
        return None

    key = f"{db_path}:{project}"
    if key not in _instances:
        _instances[key] = VectorMemoryStore(db_path=db_path, project=project)
    return _instances[key]


__all__ = [
    "get_memory_store",
    "VectorMemoryStore",
    "ReviewRecord",
    "MemoryQuery",
    "MemoryResult",
    "embed_diff",
    "embed_text",
    "get_embedder",
]
