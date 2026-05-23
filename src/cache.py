from __future__ import annotations
import hashlib
import time
from dataclasses import dataclass, field
from typing import Optional
from src.types import ReviewResult
from src.cache_backend import MemoryCache, SQLiteCache
import logging
logger = logging.getLogger(__name__)
@dataclass
class CacheEntry:
    result : ReviewResult
    expires_at: float

class ReviewCache:
    def __init__ (self, ttl_seconds: int = 300, persistent:Optional[bool] = False) -> None:
        self.ttl_seconds = ttl_seconds
        self._memory = MemoryCache()
        self._persistent: Optional[SQLiteCache] = (
            SQLiteCache() if persistent else None
        )

    @staticmethod
    def make_key(diff: str) -> str:
        return hashlib.sha256(diff.encode("utf-8")).hexdigest()
    
    def get(self, key: str) -> Optional[ReviewResult]:
        result = self._memory.get(key)
        if result is not None:
            return result
        
        if self._persistent:
            result = self._persistent.get(key)
            if result is not None:
                self._memory.set(key, result, self.ttl_seconds)
                return result
            
        return None
    
    def set(self, key: str, result: ReviewResult) -> None:
        self._memory.set(key, result, self.ttl_seconds)
        if self._persistent:
            self._persistent.set(key, result, self.ttl_seconds)

    def invalidate(self, key: str) -> None:
        self._memory.invalidate(key)
        if self._persistent:
            self._persistent.invalidate(key)

    def clear(self) -> None:
        self._memory.clear()
        if self._persistent:
            self._persistent.clear()