"""
Vector memory store using ChromaDB.
Persists review history for similarity-based retrieval.
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional

from src.memory.models import ReviewRecord, MemoryQuery, MemoryResult

logger = logging.getLogger(__name__)

COLLECTION_NAME = "review_history"


class VectorMemoryStore:
    """ChromaDB-backed vector store for review history.

    Stores ReviewRecords with their embeddings and provides
    similarity search to find past reviews with similar changesets.

    All ChromaDB errors are caught and logged — the store degrades
    gracefully without crashing the review workflow.
    """

    def __init__(self, db_path: str | Path, project: str):
        self._db_path = Path(db_path)
        self._project = project
        self._collection = None
        self._client = None

    # ── Lazy init ─────────────────────────────────────────────

    def _ensure_initialized(self):
        """Lazy-init ChromaDB client and collection on first use."""
        if self._collection is not None:
            return

        import chromadb

        self._db_path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self._db_path))

        # Get or create collection with cosine distance metric
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.debug("Vector memory initialized at %s", self._db_path)

    # ── Write ─────────────────────────────────────────────────

    def add_review(self, record: ReviewRecord) -> None:
        """Store a review record with its embedding.

        Gracefully handles errors — logs warning but does not raise.
        """
        try:
            self._ensure_initialized()

            # ChromaDB metadata must be flat: strings, numbers, or bools
            metadata = {
                "project": record.project,
                "branch": record.branch,
                "diff_hash": record.diff_hash,
                "files": ",".join(record.files),
                "summary": record.summary[:500],
                "score_total": (
                    str(record.score_total) if record.score_total is not None else ""
                ),
                "issues_count": str(record.issues_count),
                "critical_count": str(record.critical_count),
                "major_count": str(record.major_count),
                "timestamp": str(record.timestamp),
            }

            self._collection.add(
                ids=[record.id],
                embeddings=[record.embedding],
                metadatas=[metadata],
                documents=[record.summary],
            )
            logger.debug("Saved review %s to vector memory.", record.id)

        except Exception as exc:
            logger.warning("Failed to save review to vector memory: %s", exc)

    # ── Read ──────────────────────────────────────────────────

    def query_similar(self, query: MemoryQuery) -> list[MemoryResult]:
        """Find top-K reviews similar to the given query.

        Uses combined scoring: diff embedding similarity (0.6),
        file path overlap (0.3), and branch match (0.1).

        Returns empty list on any error (graceful degradation).
        """
        try:
            self._ensure_initialized()

            count = self._collection.count()
            if count == 0:
                return []

            # Fetch more than needed for reranking
            n_results = min(query.top_k * 2, count)
            results = self._collection.query(
                query_embeddings=[query.diff_embedding],
                n_results=n_results,
                include=["metadatas", "distances"],
            )

            if not results["ids"] or not results["ids"][0]:
                return []

            memory_results: list[MemoryResult] = []
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                diff_similarity = 1.0 - distance  # Convert distance to similarity

                # Parse stored file list
                stored_files_raw = metadata.get("files", "")
                stored_files = (
                    stored_files_raw.split(",") if stored_files_raw else []
                )

                # Calculate file overlap (Jaccard similarity)
                file_overlap = _jaccard_similarity(
                    set(query.files), set(stored_files)
                )

                # Branch match
                branch_match = metadata.get("branch", "") == query.branch

                # Combined score
                combined = (
                    0.6 * diff_similarity
                    + 0.3 * file_overlap
                    + 0.1 * (1.0 if branch_match else 0.0)
                )

                if combined < query.min_score:
                    continue

                # Reconstruct ReviewRecord from metadata
                record = ReviewRecord(
                    id=doc_id,
                    timestamp=float(metadata.get("timestamp", 0)),
                    project=metadata.get("project", ""),
                    branch=metadata.get("branch", ""),
                    diff_hash=metadata.get("diff_hash", ""),
                    files=stored_files,
                    summary=metadata.get("summary", ""),
                    score_total=(
                        float(metadata["score_total"])
                        if metadata.get("score_total")
                        else None
                    ),
                    issues_count=int(metadata.get("issues_count", 0)),
                    critical_count=int(metadata.get("critical_count", 0)),
                    major_count=int(metadata.get("major_count", 0)),
                )

                memory_results.append(
                    MemoryResult(
                        record=record,
                        similarity=combined,
                        diff_similarity=diff_similarity,
                        file_overlap=file_overlap,
                        branch_match=branch_match,
                    )
                )

            # Sort by combined score and take top_k
            memory_results.sort(key=lambda r: r.similarity, reverse=True)
            return memory_results[: query.top_k]

        except Exception as exc:
            logger.warning("Failed to query vector memory: %s", exc)
            return []

    # ── Maintenance ───────────────────────────────────────────

    def count(self) -> int:
        """Get number of stored reviews."""
        try:
            self._ensure_initialized()
            return self._collection.count()
        except Exception:
            return 0

    def clear(self) -> None:
        """Clear all stored reviews."""
        try:
            self._ensure_initialized()
            self._client.delete_collection(COLLECTION_NAME)
            self._collection = None
            logger.info("Vector memory cleared.")
        except Exception as exc:
            logger.warning("Failed to clear vector memory: %s", exc)


def _jaccard_similarity(set_a: set, set_b: set) -> float:
    """Calculate Jaccard similarity between two sets.

    Returns a float between 0.0 (no overlap) and 1.0 (identical sets).
    """
    if not set_a and not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0
