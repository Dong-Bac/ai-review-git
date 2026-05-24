"""
Data models for Vector Memory module.
Stores review history for similarity-based retrieval.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from src.types import ReviewResult


@dataclass
class ReviewRecord:
    """A single review record stored in vector memory."""

    id: str = field(default_factory=lambda: uuid4().hex[:12])
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    project: str = ""
    branch: str = ""
    diff_hash: str = ""  # SHA-256 of diff (links to ReviewCache)
    files: list[str] = field(default_factory=list)
    summary: str = ""  # First meaningful paragraph of review content
    score_total: Optional[float] = None  # Weighted total score (0-10)
    issues_count: int = 0
    critical_count: int = 0
    major_count: int = 0
    embedding: Optional[list[float]] = None  # 384-dim vector

    @classmethod
    def from_review_result(
        cls,
        result: ReviewResult,
        diff_hash: str,
        branch: str,
        project: str,
        files: list[str],
        embedding: list[float],
    ) -> ReviewRecord:
        """Create a ReviewRecord from a completed review result.

        Automatically extracts summary, score, and issue counts
        from the raw review content.
        """
        content = result.content.strip()

        # Extract summary: first non-header, non-table paragraph
        summary = ""
        for line in content.split("\n"):
            stripped = line.strip()
            if (
                stripped
                and not stripped.startswith("#")
                and not stripped.startswith("|")
                and not stripped.startswith("---")
                and not stripped.startswith("```")
            ):
                summary = stripped[:500]
                break

        # Parse score if available
        score_total = result.score.total if result.score else None

        # Rough issue counting via emoji markers
        issues_count = (
            content.count("🔴")
            + content.count("🟠")
            + content.count("🟡")
            + content.count("🔵")
        )
        critical_count = content.count("🔴")
        major_count = content.count("🟠")

        return cls(
            project=project,
            branch=branch,
            diff_hash=diff_hash,
            files=files,
            summary=summary,
            score_total=score_total,
            issues_count=issues_count,
            critical_count=critical_count,
            major_count=major_count,
            embedding=embedding,
        )


@dataclass
class MemoryQuery:
    """Query parameters for vector memory retrieval."""

    diff_embedding: list[float]  # Embedding of the current diff
    files: list[str]  # Files in the current changeset
    branch: str  # Current branch
    top_k: int = 3  # Number of results to return
    min_score: float = 0.5  # Minimum combined similarity threshold


@dataclass
class MemoryResult:
    """A single retrieved memory result with similarity score breakdown."""

    record: ReviewRecord
    similarity: float  # Combined similarity score (0-1)
    diff_similarity: float  # Cosine similarity of diff embeddings
    file_overlap: float  # Jaccard similarity of file paths
    branch_match: bool  # Whether same branch
