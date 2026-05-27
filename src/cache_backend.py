
from __future__ import annotations
import atexit
import hashlib
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.types import ReviewResult
import logging
logger = logging.getLogger(__name__)

#-------Abstract interface---------------

class CacheBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[ReviewResult]:
        ...

    @abstractmethod
    def set(self, key: str, result: ReviewResult, ttl: int) -> None:
        ...
    
    @abstractmethod
    def invalidate(self, key: str) -> None:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...


# -------- In-memory backend-------

@dataclass
class _CacheEntry:
    result: ReviewResult
    expires_at: float


class MemoryCache(CacheBackend):
    def __init__(self):
        self._store: dict[str, _CacheEntry] = {}

    
    def get(self, key: str) -> Optional[ReviewResult]:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.monotonic() > entry.expires_at:
            del self._store[key]
            return None
        return entry.result
    
    def set(self, key: str, result: ReviewResult, ttl: int) -> None:
        self._store[key] = _CacheEntry(
            result=result,
            expires_at=time.monotonic() + ttl,
        )

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

#--- sqLite--------

class SQLiteCache(CacheBackend):
    DB_FILENAME = ".ai-review-cache.db"

    def __init__(self, db_path: Optional[Path] = None) -> None:
        import sqlite3

        
        self._db_path = db_path or Path.cwd() / self.DB_FILENAME
        self._conn = sqlite3.connect(self._db_path)
        self._conn.execute(
            """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    model TEXT NOT NULL,
                    tokens_used INTEGER,
                    expires_at REAL NOT NULL
                )
            """
        )

        self._conn.commit()

        self._conn.execute(
            "DELETE FROM cache WHERE expires_at <= ?",
            (time.time(),),
        )
        self._conn.commit()

        # Register cleanup on interpreter exit to prevent connection leak
        atexit.register(self.close)

    def get(self, key: str) -> Optional[ReviewResult]:
        import sqlite3
        try:
            row = self._conn.execute(
                "SELECT content, model, tokens_used, expires_at FROM cache WHERE key = ?",
                 (key,),
            ).fetchone()
        except sqlite3.OperationalError:
            return None
        
        if row is None:
            return  None
        
        content, model, tokens_used, expires_at = row

        if time.time() > expires_at:
            self._conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            self._conn.commit()
            return None
        
        return ReviewResult(
            content= content,
            model= model,
            tokens_used= tokens_used
        )
    
    def set(self, key: str, result: ReviewResult, ttl: int) -> None:
        import sqlite3
        
        try:
            self._conn.execute(
                 """
                INSERT OR REPLACE INTO cache (key, content, model, tokens_used, expires_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    key,
                    result.content,
                    result.model,
                    result.tokens_used,
                    time.time() + ttl,
                ),
            )
            self._conn.commit()
        except sqlite3.OperationalError:
            pass

    def invalidate(self, key: str) -> None:
        self._conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        self._conn.commit()

    def clear(self) -> None:
        self._conn.execute("DELETE FROM cache")
        self._conn.commit()

    def close(self) -> None:
        """Đóng kết nối SQLite (gọi khi app kết thúc)."""
        try:
            self._conn.close()
        except Exception:
            pass

    def __del__(self) -> None:
        """Destructor — đảm bảo connection được đóng."""
        self.close()

    def __enter__(self) -> SQLiteCache:
        return self

    def __exit__(self, *args) -> None:
        self.close()
        
