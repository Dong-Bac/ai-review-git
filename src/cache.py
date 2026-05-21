from __future__ import annotations
import hashlib
import time
from dataclasses import dataclass, field
from typing import Optional
from src.types import ReviewResult

@dataclass
class CacheEntry:
    result : ReviewResult
    expires_at: float

class ReviewCache:
    def __init__ (self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self._store : dict[str, CacheEntry] = {}

    @staticmethod
    def make_key(diff: str) -> str:
        return hashlib.sha256(diff.encode("utf-8")).hexdigest()
    
    def get(self, key: str) -> Optional[ReviewResult]:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.monotonic() > entry.expires_at:
            del self._store[key]
            return None
        return entry.result
    
    def set(self, key: str, result: ReviewResult) -> None:
        self._store[key] = CacheEntry(
            result = result,
            expires_at= time.monotonic() + self.ttl_seconds
        )

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()