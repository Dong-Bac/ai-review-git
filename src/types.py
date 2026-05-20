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
class ReviewResult:
    content: str
    model: str
    tokens_used: Optional[int] = None


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
