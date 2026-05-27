"""
Tests for cache backends: MemoryCache and SQLiteCache.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from src.cache_backend import MemoryCache, SQLiteCache
from src.types import ReviewResult


class TestMemoryCache:
    """Tests for in-memory cache backend."""

    def test_set_and_get(self):
        cache = MemoryCache()
        result = ReviewResult(content="test review", model="deepseek-chat")

        cache.set("key1", result, ttl=300)
        cached = cache.get("key1")

        assert cached is not None
        assert cached.content == "test review"
        assert cached.model == "deepseek-chat"

    def test_get_missing_key(self):
        cache = MemoryCache()
        assert cache.get("nonexistent") is None

    def test_get_expired_entry(self):
        cache = MemoryCache()
        result = ReviewResult(content="expired", model="deepseek-chat")

        # Set with 0 TTL so it expires immediately
        cache.set("expired_key", result, ttl=0)
        time.sleep(0.01)  # Ensure time passes
        assert cache.get("expired_key") is None

    def test_invalidate(self):
        cache = MemoryCache()
        result = ReviewResult(content="to delete", model="deepseek-chat")

        cache.set("delete_me", result, ttl=300)
        assert cache.get("delete_me") is not None

        cache.invalidate("delete_me")
        assert cache.get("delete_me") is None

    def test_invalidate_nonexistent(self):
        cache = MemoryCache()
        cache.invalidate("nothing")  # Should not raise

    def test_clear(self):
        cache = MemoryCache()
        cache.set("a", ReviewResult(content="a", model="m"), ttl=300)
        cache.set("b", ReviewResult(content="b", model="m"), ttl=300)

        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_multiple_keys_independent(self):
        cache = MemoryCache()
        cache.set("k1", ReviewResult(content="v1", model="m"), ttl=300)
        cache.set("k2", ReviewResult(content="v2", model="m"), ttl=300)

        assert cache.get("k1").content == "v1"
        assert cache.get("k2").content == "v2"

    def test_tokens_used_preserved(self):
        cache = MemoryCache()
        result = ReviewResult(content="test", model="m", tokens_used=123)

        cache.set("tokens", result, ttl=300)
        cached = cache.get("tokens")

        assert cached.tokens_used == 123


class TestSQLiteCache:
    """Tests for SQLite persistent cache backend."""

    @pytest.fixture
    def db_path(self, tmp_path: Path) -> Path:
        return tmp_path / "test-cache.db"

    @pytest.fixture
    def cache(self, db_path: Path) -> SQLiteCache:
        c = SQLiteCache(db_path=db_path)
        yield c
        c.close()

    def test_set_and_get(self, cache: SQLiteCache):
        result = ReviewResult(content="persistent review", model="deepseek-chat")

        cache.set("pkey1", result, ttl=300)
        cached = cache.get("pkey1")

        assert cached is not None
        assert cached.content == "persistent review"
        assert cached.model == "deepseek-chat"

    def test_get_missing_key(self, cache: SQLiteCache):
        assert cache.get("nonexistent") is None

    def test_get_expired_entry(self, db_path: Path):
        cache = SQLiteCache(db_path=db_path)
        result = ReviewResult(content="expired", model="deepseek-chat")

        cache.set("expired_key", result, ttl=-1)  # Negative TTL = already expired
        cached = cache.get("expired_key")
        cache.close()

        assert cached is None

    def test_invalidate(self, cache: SQLiteCache):
        result = ReviewResult(content="to delete", model="deepseek-chat")

        cache.set("delete_me", result, ttl=300)
        assert cache.get("delete_me") is not None

        cache.invalidate("delete_me")
        assert cache.get("delete_me") is None

    def test_clear(self, cache: SQLiteCache):
        cache.set("a", ReviewResult(content="a", model="m"), ttl=300)
        cache.set("b", ReviewResult(content="b", model="m"), ttl=300)

        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_tokens_used_preserved(self, cache: SQLiteCache):
        result = ReviewResult(content="test", model="m", tokens_used=456)

        cache.set("tokens", result, ttl=300)
        cached = cache.get("tokens")

        assert cached.tokens_used == 456

    def test_persistence_across_instances(self, db_path: Path):
        """Verify data survives cache instance recreation."""
        cache1 = SQLiteCache(db_path=db_path)
        cache1.set("persist", ReviewResult(content="survived", model="m"), ttl=300)
        cache1.close()

        cache2 = SQLiteCache(db_path=db_path)
        cached = cache2.get("persist")
        cache2.close()

        assert cached is not None
        assert cached.content == "survived"

    def test_context_manager(self, db_path: Path):
        """Test __enter__ / __exit__ protocol."""
        with SQLiteCache(db_path=db_path) as cache:
            cache.set("ctx", ReviewResult(content="ctx test", model="m"), ttl=300)
            assert cache.get("ctx").content == "ctx test"

    def test_update_existing_key(self, cache: SQLiteCache):
        """Insert OR REPLACE behavior."""
        cache.set("update", ReviewResult(content="old", model="m"), ttl=300)
        cache.set("update", ReviewResult(content="new", model="m"), ttl=300)

        cached = cache.get("update")
        assert cached.content == "new"
