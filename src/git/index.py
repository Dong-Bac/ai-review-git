"""
Git utilities — thin async wrappers around GitPython.
"""

from __future__ import annotations
import asyncio
from pathlib import Path

import git
from git import InvalidGitRepositoryError, Repo

from src.types import ChangedFile, FileStatus, GitDiffInfo


def _status_to_enum(status_char: str) -> FileStatus:
    mapping: dict[str, FileStatus] = {
        "A": "added",
        "M": "modified",
        "D": "deleted",
        "R": "renamed",
    }
    return mapping.get(status_char.upper(), "unknown")


async def is_git_repository(root: Path) -> bool:
    """Return True if root is inside a git repository."""
    try:
        await asyncio.to_thread(Repo, root, search_parent_directories=True)
        return True
    except InvalidGitRepositoryError:
        return False


async def get_current_branch(root: Path) -> str:
    """Return the active branch name."""
    try:
        repo = await asyncio.to_thread(Repo, root, search_parent_directories=True)
        return repo.active_branch.name
    except Exception:
        return "unknown"


async def get_staged_diff(root: Path) -> str:
    """Return the raw staged diff (git diff --cached)."""
    def _diff() -> str:
        repo = Repo(root, search_parent_directories=True)
        return repo.git.diff("--cached")

    return await asyncio.to_thread(_diff)


async def get_staged_files(root: Path) -> list[ChangedFile]:
    """Return list of staged changed files with their status.

    Uses a single ``git diff --cached --name-status`` call which correctly
    handles all scenarios:
    - New files (added to index, not yet in HEAD)
    - Modified files
    - Deleted files
    - Renamed files
    - Empty repository (no commits yet)
    """
    def _files() -> list[ChangedFile]:
        repo = Repo(root, search_parent_directories=True)
        # Single authoritative call — works for both new & existing repos
        output = repo.git.diff("--cached", "--name-status")
        files: list[ChangedFile] = []
        for line in output.splitlines():
            if not line.strip():
                continue
            # Format: <status>\t<path>  or  <status>\t<old_path>\t<new_path> (rename)
            parts = line.split("\t")
            status_char = parts[0][0]  # A, M, D, R, C, etc.
            # For renames (Rxxx), the last part is the current path
            path = parts[-1]
            files.append(ChangedFile(
                path=path,
                status=_status_to_enum(status_char),
            ))
        return files

    try:
        return await asyncio.to_thread(_files)
    except Exception:
        # Fallback: parse git status --porcelain
        return await _get_staged_files_porcelain(root)


async def _get_staged_files_porcelain(root: Path) -> list[ChangedFile]:
    """Fallback: parse ``git status --porcelain`` output.

    Format: ``XY <path>`` where X = index status, Y = working tree status.
    Uses ``split(maxsplit=1)`` instead of hardcoded indices to handle
    filenames with spaces correctly.
    """
    def _run() -> list[ChangedFile]:
        repo = Repo(root, search_parent_directories=True)
        output = repo.git.status("--porcelain")
        files: list[ChangedFile] = []
        for line in output.splitlines():
            if not line:
                continue
            index_status = line[0]
            # Split on first space to get the path reliably
            # (handles filenames with spaces)
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue
            filepath = parts[1].strip()
            if index_status != " " and index_status != "?":
                files.append(ChangedFile(
                    path=filepath,
                    status=_status_to_enum(index_status),
                ))
        return files

    return await asyncio.to_thread(_run)


async def get_git_diff_info(root: Path) -> GitDiffInfo:
    """High-level function: gather all git info needed for review."""
    diff, changed_files, branch = await asyncio.gather(
        get_staged_diff(root),
        get_staged_files(root),
        get_current_branch(root),
    )

    return GitDiffInfo(
        diff=diff,
        changed_files=changed_files,
        branch=branch,
        is_empty=diff.strip() == "" and len(changed_files) == 0,
    )
