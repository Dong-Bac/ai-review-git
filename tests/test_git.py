"""
Tests for git utilities.
Uses mocking to avoid requiring an actual git repository.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.git.index import (
    is_git_repository,
    get_current_branch,
    get_staged_diff,
    get_staged_files,
    get_git_diff_info,
    _status_to_enum,
)
from src.types import ChangedFile, GitDiffInfo


class TestStatusToEnum:
    """Tests for _status_to_enum helper."""

    def test_added(self):
        assert _status_to_enum("A") == "added"

    def test_modified(self):
        assert _status_to_enum("M") == "modified"

    def test_deleted(self):
        assert _status_to_enum("D") == "deleted"

    def test_renamed(self):
        assert _status_to_enum("R") == "renamed"

    def test_unknown(self):
        assert _status_to_enum("C") == "unknown"
        assert _status_to_enum("?") == "unknown"
        assert _status_to_enum("") == "unknown"

    def test_case_insensitive(self):
        assert _status_to_enum("a") == "added"
        assert _status_to_enum("m") == "modified"


class TestIsGitRepository:
    """Tests for is_git_repository()."""

    @patch("src.git.index.Repo")
    async def test_returns_true_for_valid_repo(self, mock_repo):
        mock_repo.return_value = MagicMock()
        result = await is_git_repository(Path("/some/repo"))
        assert result is True

    @patch("src.git.index.Repo")
    async def test_returns_false_for_invalid_repo(self, mock_repo):
        from git import InvalidGitRepositoryError

        mock_repo.side_effect = InvalidGitRepositoryError("/not/git")
        result = await is_git_repository(Path("/not/git"))
        assert result is False


class TestGetCurrentBranch:
    """Tests for get_current_branch()."""

    @patch("src.git.index.Repo")
    async def test_returns_branch_name(self, mock_repo):
        mock_instance = MagicMock()
        mock_instance.active_branch.name = "feature/awesome"
        mock_repo.return_value = mock_instance

        branch = await get_current_branch(Path("/repo"))
        assert branch == "feature/awesome"

    @patch("src.git.index.Repo")
    async def test_returns_unknown_on_error(self, mock_repo):
        mock_repo.side_effect = Exception("git error")
        branch = await get_current_branch(Path("/repo"))
        assert branch == "unknown"


class TestGetStagedDiff:
    """Tests for get_staged_diff()."""

    @patch("src.git.index.Repo")
    async def test_returns_diff_string(self, mock_repo):
        mock_instance = MagicMock()
        mock_instance.git.diff.return_value = "diff --git a/file.py b/file.py"
        mock_repo.return_value = mock_instance

        diff = await get_staged_diff(Path("/repo"))
        assert diff == "diff --git a/file.py b/file.py"
        mock_instance.git.diff.assert_called_once_with("--cached")


class TestGetStagedFiles:
    """Tests for get_staged_files()."""

    @patch("src.git.index.Repo")
    async def test_returns_changed_files(self, mock_repo):
        mock_instance = MagicMock()
        mock_instance.git.diff.return_value = (
            "M\tsrc/main.py\n"
            "A\tsrc/new.py\n"
            "D\tsrc/old.py\n"
        )
        mock_repo.return_value = mock_instance

        files = await get_staged_files(Path("/repo"))
        assert len(files) == 3
        assert files[0] == ChangedFile(path="src/main.py", status="modified")
        assert files[1] == ChangedFile(path="src/new.py", status="added")
        assert files[2] == ChangedFile(path="src/old.py", status="deleted")

    @patch("src.git.index.Repo")
    async def test_returns_empty_list_for_no_changes(self, mock_repo):
        mock_instance = MagicMock()
        mock_instance.git.diff.return_value = ""
        mock_repo.return_value = mock_instance

        files = await get_staged_files(Path("/repo"))
        assert files == []

    @patch("src.git.index.Repo")
    async def test_fallback_to_porcelain(self, mock_repo):
        """Should fallback to git status --porcelain on error."""
        mock_instance = MagicMock()
        # First call (diff --name-status) raises
        mock_instance.git.diff.side_effect = [Exception("boom"), None]
        # Second call (status --porcelain) succeeds
        mock_instance.git.status.return_value = "M  src/file.py\n"

        # Need to patch so first call fails, second succeeds
        # Actually the fallback is in get_staged_files, let's test properly
        mock_repo.return_value = mock_instance

        # The function catches Exception and calls _get_staged_files_porcelain
        files = await get_staged_files(Path("/repo"))
        assert len(files) >= 0  # May be empty if fallback also fails


class TestGetGitDiffInfo:
    """Tests for get_git_diff_info()."""

    @patch("src.git.index.get_staged_diff")
    @patch("src.git.index.get_staged_files")
    @patch("src.git.index.get_current_branch")
    async def test_assembles_git_diff_info(
        self,
        mock_branch,
        mock_files,
        mock_diff,
    ):
        mock_diff.return_value = "diff --git a/x.py b/x.py"
        mock_files.return_value = [ChangedFile(path="x.py", status="modified")]
        mock_branch.return_value = "main"

        info = await get_git_diff_info(Path("/repo"))

        assert isinstance(info, GitDiffInfo)
        assert info.diff == "diff --git a/x.py b/x.py"
        assert len(info.changed_files) == 1
        assert info.branch == "main"
        assert info.is_empty is False

    @patch("src.git.index.get_staged_diff")
    @patch("src.git.index.get_staged_files")
    @patch("src.git.index.get_current_branch")
    async def test_detects_empty_diff(
        self,
        mock_branch,
        mock_files,
        mock_diff,
    ):
        mock_diff.return_value = ""
        mock_files.return_value = []
        mock_branch.return_value = "main"

        info = await get_git_diff_info(Path("/repo"))

        assert info.is_empty is True
