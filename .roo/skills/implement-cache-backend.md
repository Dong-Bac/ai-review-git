# Skill: Implement New Cache Backend

> Adds a new cache backend (e.g., Redis, File-based) to the caching layer.

## Trigger

When user says: "add [name] cache backend" or "implement persistent cache with [name]"

## Steps

### 1. Read Reference Files
- [`.roo/templates/new-cache-backend.md`](../templates/new-cache-backend.md) — Follow template
- [`src/cache_backend.py`](../../src/cache_backend.py:1) — Existing backends + interface
- [`src/cache.py`](../../src/cache.py:1) — How backends are wired
- [`src/types.py`](../../src/types.py:1) — `ReviewResult` type

### 2. Implement CacheBackend

Add to [`src/cache_backend.py`](../../src/cache_backend.py:1):

```python
class NewBackend(CacheBackend):
    def __init__(self, ...):
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

### 3. Wire into ReviewCache

Edit [`src/cache.py`](../../src/cache.py:1) to accept and use the new backend.

### 4. Add CLI Option (if user-selectable)

Edit [`src/index.py`](../../src/index.py:1) to add `--cache-backend` option.

### 5. Verify

- [ ] Implements all 4 `CacheBackend` methods
- [ ] TTL expiry handled correctly
- [ ] Wired into `ReviewCache` with fallback
- [ ] Error handling for connection/storage failures
- [ ] CLI option added (if applicable)
