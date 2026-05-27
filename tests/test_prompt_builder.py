"""
Tests for prompt builder.
"""

from __future__ import annotations

import pytest

from src.ai.prompt_builder import build_prompt
from src.types import ReviewContext, ProjectInfo, ChangedFile


@pytest.fixture
def sample_context() -> ReviewContext:
    return ReviewContext(
        diff="diff --git a/src/main.py b/src/main.py\nindex abc..def\n--- a/src/main.py\n+++ b/src/main.py\n@@ -1 +1 @@\n-print('old')\n+print('new')",
        changed_files=[
            ChangedFile(path="src/main.py", status="modified", content="print('new')\n"),
        ],
        branch="feature/test",
        rules="",
        project_info=ProjectInfo(name="test-project", root_path="/tmp/test"),
    )


class TestBuildPrompt:
    """Tests for build_prompt()."""

    def test_returns_prompt_object(self, sample_context: ReviewContext):
        prompt = build_prompt(sample_context)

        assert prompt.system is not None
        assert prompt.user is not None

    def test_system_prompt_contains_default_rules(self, sample_context: ReviewContext):
        """System prompt should include default rules when no custom rules."""
        prompt = build_prompt(sample_context)

        assert "Tính đúng đắn" in prompt.system
        assert "Bảo mật" in prompt.system
        assert "Hiệu suất" in prompt.system

    def test_system_prompt_includes_custom_rules(self):
        """Custom rules should appear in system prompt instead of defaults."""
        ctx = ReviewContext(
            diff="dummy diff",
            changed_files=[],
            branch="main",
            rules="## Custom Rule\n- Always use type hints",
            project_info=ProjectInfo(name="test", root_path="/tmp"),
        )
        prompt = build_prompt(ctx)

        # Custom rule should be present
        assert "Always use type hints" in prompt.system
        # Default rules section header should NOT be present (custom overrides)
        assert "### 1. Tính đúng đắn" not in prompt.system

    def test_user_prompt_contains_diff(self, sample_context: ReviewContext):
        prompt = build_prompt(sample_context)

        assert "diff --git a/src/main.py b/src/main.py" in prompt.user

    def test_user_prompt_contains_project_info(self, sample_context: ReviewContext):
        prompt = build_prompt(sample_context)

        assert "test-project" in prompt.user
        assert "feature/test" in prompt.user

    def test_user_prompt_contains_changed_files(self, sample_context: ReviewContext):
        prompt = build_prompt(sample_context)

        assert "src/main.py" in prompt.user
        assert "[modified]" in prompt.user

    def test_user_prompt_contains_file_contents(self, sample_context: ReviewContext):
        prompt = build_prompt(sample_context)

        assert "print('new')" in prompt.user

    def test_empty_changed_files(self):
        """Should handle empty changed files gracefully."""
        ctx = ReviewContext(
            diff="",
            changed_files=[],
            branch="main",
            rules="",
            project_info=ProjectInfo(name="test", root_path="/tmp"),
        )
        prompt = build_prompt(ctx)

        assert prompt.system is not None
        assert prompt.user is not None

    def test_deleted_file_excluded_from_contents(self):
        """Deleted files should not appear in file contents section."""
        ctx = ReviewContext(
            diff="diff --git a/src/old.py b/src/old.py",
            changed_files=[
                ChangedFile(path="src/old.py", status="deleted", content="old content"),
            ],
            branch="main",
            rules="",
            project_info=ProjectInfo(name="test", root_path="/tmp"),
        )
        prompt = build_prompt(ctx)

        assert "old content" not in prompt.user

    def test_user_prompt_contains_review_instructions(self, sample_context: ReviewContext):
        prompt = build_prompt(sample_context)

        assert "Chấm điểm tổng thể" in prompt.user
        assert "thang 10" in prompt.user
