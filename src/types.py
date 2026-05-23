"""
Core domain types for ai-review.
Using dataclasses for lightweight, type-safe value objects.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Optional

FileStatus = Literal["added", "modified", "deleted", "renamed", "unknown"]


@dataclass
class ChangedFile:
    path: str
    status: FileStatus
    content: Optional[str] = None  # Populated after file reading


@dataclass
class GitDiffInfo:
    diff: str
    changed_files: list[ChangedFile]
    branch: str
    is_empty: bool


@dataclass
class ProjectInfo:
    name: str
    root_path: str


@dataclass
class ReviewContext:
    diff: str
    changed_files: list[ChangedFile]
    branch: str
    rules: str           # Contents of .roo/rules.md (empty string if absent)
    project_info: ProjectInfo


@dataclass
class Prompt:
    system: str
    user: str


@dataclass
class ReviewScore:
    """Scoring breakdown for a code review (0-10 scale per criterion)."""
    correctness: float      # Weight: 3.0
    security: float         # Weight: 2.0
    performance: float      # Weight: 1.5
    quality: float          # Weight: 2.0
    maintainability: float  # Weight: 1.5

    @property
    def total(self) -> float:
        """Calculate weighted total score out of 10."""
        return (
            self.correctness * 3.0
            + self.security * 2.0
            + self.performance * 1.5
            + self.quality * 2.0
            + self.maintainability * 1.5
        ) / 10.0


@dataclass
class ReviewResult:
    content: str
    model: str
    tokens_used: Optional[int] = None
    score: Optional[ReviewScore] = None  # Parsed from AI response (optional)


@dataclass
class AppConfig:
    api_key: str
    model: str
    base_url: str
    app_name: str
    app_url: str
    max_tokens: int
    provider: str = field(default="deepseek")

@dataclass
class StreamChunk:
    content: str
    finish_reason: Optional[str] = None
