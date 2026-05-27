"""
Tests for memory models: ReviewRecord, MemoryQuery, MemoryResult.
"""

from __future__ import annotations

from src.memory.models import ReviewRecord, MemoryQuery, MemoryResult
from src.types import ReviewResult, ReviewScore


class TestReviewRecord:
    """Tests for ReviewRecord dataclass."""

    def test_default_id_is_generated(self):
        record = ReviewRecord()
        assert record.id is not None
        assert len(record.id) == 12  # uuid4().hex[:12]

    def test_default_timestamp_is_set(self):
        record = ReviewRecord()
        assert record.timestamp > 0

    def test_default_values(self):
        record = ReviewRecord()
        assert record.project == ""
        assert record.branch == ""
        assert record.diff_hash == ""
        assert record.files == []
        assert record.summary == ""
        assert record.score_total is None
        assert record.issues_count == 0
        assert record.critical_count == 0
        assert record.major_count == 0
        assert record.embedding is None

    def test_from_review_result_basic(self):
        result = ReviewResult(
            content="This is a great changeset. Everything looks good.",
            model="deepseek-chat",
        )
        record = ReviewRecord.from_review_result(
            result=result,
            diff_hash="abc123",
            branch="main",
            project="my-project",
            files=["src/main.py"],
            embedding=[0.1, 0.2, 0.3],
        )

        assert record.project == "my-project"
        assert record.branch == "main"
        assert record.diff_hash == "abc123"
        assert record.files == ["src/main.py"]
        assert record.embedding == [0.1, 0.2, 0.3]
        assert record.summary == "This is a great changeset. Everything looks good."
        assert record.score_total is None
        assert record.issues_count == 0

    def test_from_review_result_with_score(self):
        result = ReviewResult(
            content="Good code.",
            model="deepseek-chat",
            score=ReviewScore(
                correctness=9.0,
                security=8.0,
                performance=7.0,
                quality=8.0,
                maintainability=7.0,
            ),
        )
        record = ReviewRecord.from_review_result(
            result=result,
            diff_hash="def456",
            branch="feature/x",
            project="p",
            files=["a.py"],
            embedding=[0.5, 0.6],
        )

        assert record.score_total is not None
        assert record.score_total > 0

    def test_from_review_result_counts_issues(self):
        content = """🔴 Critical bug found
🟠 Major performance issue
🟡 Minor style nitpick
🔵 Info suggestion"""
        result = ReviewResult(content=content, model="deepseek-chat")
        record = ReviewRecord.from_review_result(
            result=result,
            diff_hash="h",
            branch="b",
            project="p",
            files=["f.py"],
            embedding=[0.1],
        )

        assert record.issues_count == 4
        assert record.critical_count == 1
        assert record.major_count == 1

    def test_from_review_result_skips_headers_in_summary(self):
        content = """
# Header

| Table | Row |
|-------|-----|
| data  | val |

---
The actual summary starts here.
"""
        result = ReviewResult(content=content, model="deepseek-chat")
        record = ReviewRecord.from_review_result(
            result=result,
            diff_hash="h",
            branch="b",
            project="p",
            files=["f.py"],
            embedding=[0.1],
        )

        assert "The actual summary starts here" in record.summary
        assert "Header" not in record.summary


class TestMemoryQuery:
    """Tests for MemoryQuery dataclass."""

    def test_default_values(self):
        query = MemoryQuery(
            diff_embedding=[0.1, 0.2],
            files=["src/main.py"],
            branch="main",
        )

        assert query.diff_embedding == [0.1, 0.2]
        assert query.files == ["src/main.py"]
        assert query.branch == "main"
        assert query.top_k == 3  # default
        assert query.min_score == 0.5  # default

    def test_custom_values(self):
        query = MemoryQuery(
            diff_embedding=[0.5],
            files=["a.py", "b.py"],
            branch="feature/x",
            top_k=5,
            min_score=0.3,
        )

        assert query.top_k == 5
        assert query.min_score == 0.3


class TestMemoryResult:
    """Tests for MemoryResult dataclass."""

    def test_all_fields(self):
        record = ReviewRecord(
            id="test123",
            project="p",
            branch="main",
            diff_hash="h",
            files=["f.py"],
            summary="summary",
        )
        result = MemoryResult(
            record=record,
            similarity=0.85,
            diff_similarity=0.9,
            file_overlap=0.5,
            branch_match=True,
        )

        assert result.record.id == "test123"
        assert result.similarity == 0.85
        assert result.diff_similarity == 0.9
        assert result.file_overlap == 0.5
        assert result.branch_match is True
