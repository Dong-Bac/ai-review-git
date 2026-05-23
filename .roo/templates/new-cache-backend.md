# New Cache Backend Template

> Template for adding a new cache backend to [`src/cache_backend.py`](../../src/cache_backend.py:1).

## Steps

### 1. Implement CacheBackend Interface

```python
class RedisCache(CacheBackend):
    def __init__(self, ...):
        # Initialize connection
        ...

    def get(self, key: str) -> Optional[ReviewResult]:
        ...

    def set(self, key: str, result: ReviewResult, ttl: int) -> None:
        ...

    def invalidate(self, key: str) -> None:
        ...

    def clear(self) -> None:
        ...
```

### 2. Wire into ReviewCache

Edit [`src/cache.py`](../../src/cache.py:1):

```python
class ReviewCache:
    def __init__(self, ttl_seconds: int = 300, backend: str = "memory"):
        self._memory = MemoryCache()
        if backend == "redis":
            self._persistent = RedisCache()
        elif backend == "sqlite":
            self._persistent = SQLiteCache()
        else:
            self._persistent = None
```

## CacheBackend Interface

```python
class CacheBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[ReviewResult]: ...
    @abstractmethod
    def set(self, key: str, result: ReviewResult, ttl: int) -> None: ...
    @abstractmethod
    def invalidate(self, key: str) -> None: ...
    @abstractmethod
    def clear(self) -> None: ...
```

## Key Design Rules

1. **Two-tier cache**: Memory (fast) → Persistent (durable)
2. **TTL-based expiry**: Each entry has `expires_at` timestamp
3. **Cache key**: SHA-256 hash of git diff string
4. **Graceful degradation**: Cache failure should not crash the app
5. **Thread-safe**: Use appropriate locks for concurrent access

## Checklist

- [ ] Implements all 4 methods of `CacheBackend`
- [ ] TTL expiry handled (expired entries return `None`)
- [ ] Wired into `ReviewCache` with fallback
- [ ] Added to CLI options if user-selectable
- [ ] Error handling (OperationalError, connection failures)
