"""
Tests for ReviewCache (the high-level cache orchestrator).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.cache import ReviewCache
from src.types import ReviewResult


class TestReviewCache:
    """Tests for ReviewCache."""

    def test_make_key_consistency(self):
        """Same diff should produce same key."""
        diff = "diff --git a/file.py b/file.py"
        key1 = ReviewCache.make_key(diff)
        key2 = ReviewCache.make_key(diff)
        assert key1 == key2

    def test_make_key_different_diffs(self):
        """Different diffs should produce different keys."""
        key1 = ReviewCache.make_key("diff a")
        key2 = ReviewCache.make_key("diff b")
        assert key1 != key2

    def test_set_and_get_memory_only(self):
        cache = ReviewCache(ttl_seconds=300, persistent=False)
        result = ReviewResult(content="test", model="deepseek-chat")
        key = ReviewCache.make_key("some diff")

        cache.set(key, result)
        cached = cache.get(key)

        assert cached is not None
        assert cached.content == "test"

    def test_get_missing_key(self):
        cache = ReviewCache(ttl_seconds=300, persistent=False)
        assert cache.get("nonexistent") is None

    def test_invalidate(self):
        cache = ReviewCache(ttl_seconds=300, persistent=False)
        result = ReviewResult(content="test", model="deepseek-chat")
        key = ReviewCache.make_key("diff")

        cache.set(key, result)
        assert cache.get(key) is not None

        cache.invalidate(key)
        assert cache.get(key) is None

    def test_clear(self):
        cache = ReviewCache(ttl_seconds=300, persistent=False)
        cache.set("a", ReviewResult(content="a", model="m"))
        cache.set("b", ReviewResult(content="b", model="m"))

        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_persistent_cache_fallback(self, tmp_path: Path):
        """With persistent=True, should fall back to SQLite if memory misses."""
        from src.cache_backend import SQLiteCache

        # We can't easily test the two-tier fallback without mocking,
        # but we can verify persistent mode doesn't crash
        cache = ReviewCache(ttl_seconds=300, persistent=True)
        result = ReviewResult(content="persistent test", model="deepseek-chat")
        key = ReviewCache.make_key("persistent diff")

        cache.set(key, result)
        cached = cache.get(key)

        assert cached is not None
        assert cached.content == "persistent test"
        cache.clear()

    def test_ttl_respected(self):
        """Cache with 0 TTL should expire immediately."""
        cache = ReviewCache(ttl_seconds=0, persistent=False)
        result = ReviewResult(content="expired", model="deepseek-chat")
        key = ReviewCache.make_key("expiring diff")

        cache.set(key, result)
        # With 0 TTL, the entry expires immediately
        import time
        time.sleep(0.01)
        cached = cache.get(key)

        assert cached is None
