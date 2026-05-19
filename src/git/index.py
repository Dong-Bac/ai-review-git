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
    """Return list of staged changed files with their status."""
    def _files() -> list[ChangedFile]:
        repo = Repo(root, search_parent_directories=True)
        files: list[ChangedFile] = []
        seen: set[str] = set()

        # Staged vs HEAD (or empty tree for new repos)
        try:
            head_commit = repo.head.commit
            diffs = head_commit.diff("HEAD")
        except Exception:
            diffs = []

        # Use git status for accuracy
        for item in repo.index.diff("HEAD"):
            if item.a_path not in seen:
                seen.add(item.a_path)
                files.append(ChangedFile(
                    path=item.a_path,
                    status=_status_to_enum(item.change_type),
                ))

        # New files staged but not yet in HEAD
        for path in repo.untracked_files:
            pass  # untracked are not staged

        # Staged new files (added to index, not in HEAD)
        try:
            staged = repo.index.diff(repo.head.commit)
        except Exception:
            staged = repo.index.diff(None)

        for item in staged:
            fp = item.b_path or item.a_path
            if fp and fp not in seen:
                seen.add(fp)
                files.append(ChangedFile(
                    path=fp,
                    status=_status_to_enum(item.change_type),
                ))

        return files

    try:
        return await asyncio.to_thread(_files)
    except Exception:
        # Fallback: parse git status --porcelain
        return await _get_staged_files_porcelain(root)


async def _get_staged_files_porcelain(root: Path) -> list[ChangedFile]:
    """Fallback: parse `git status --porcelain` output."""
    def _run() -> list[ChangedFile]:
        repo = Repo(root, search_parent_directories=True)
        output = repo.git.status("--porcelain")
        files: list[ChangedFile] = []
        for line in output.splitlines():
            if not line:
                continue
            index_status = line[0]
            filepath = line[3:].strip()
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
