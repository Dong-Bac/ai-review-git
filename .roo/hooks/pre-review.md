# Pre-Review Hook — Code Review Checklist

> Loaded when performing code review on this project.
> Ensures reviews are consistent, thorough, and aligned with project goals.

## 📋 Review Checklist

### 1. Architecture & Design
- [ ] Does the code follow the module responsibilities defined in [`src/types.py`](../../src/types.py:1)?
- [ ] Is business logic separated from CLI entry points?
- [ ] Are new features added as new commands in [`src/index.py`](../../src/index.py:1)?
- [ ] Does the change respect the cache layer ([`src/cache.py`](../../src/cache.py:1))?
- [ ] Is the provider factory pattern maintained ([`src/ai/__init__.py`](../../src/ai/__init__.py:1))?

### 2. Type Safety
- [ ] Are all new types defined as dataclasses in [`src/types.py`](../../src/types.py:1)?
- [ ] Are all function signatures fully annotated?
- [ ] Are `Optional` types used correctly (not `Optional[str] = ""`)?
- [ ] Are `Literal` types used for constrained string values?

### 3. Async Correctness
- [ ] Are all I/O operations async (using `asyncio.to_thread` or async libraries)?
- [ ] Is `asyncio.gather` used with `return_exceptions=True`?
- [ ] Are there any blocking calls in async functions?

### 4. Error Handling
- [ ] Are all `except` clauses specific (not bare `except:`)?
- [ ] Are error messages user-friendly (not raw tracebacks)?
- [ ] Is `SystemExit(1)` used for fatal errors?
- [ ] Are network timeouts set on all HTTP calls?

### 5. Security
- [ ] Are API keys loaded from env, never hardcoded?
- [ ] Are file paths sanitized to prevent traversal?
- [ ] Is input validation performed on CLI args?
- [ ] Are secrets excluded from error messages and logs?

### 6. Performance
- [ ] Are file reads concurrent via `asyncio.gather`?
- [ ] Is content truncation applied before AI calls?
- [ ] Is caching used appropriately?
- [ ] Are there any N+1 patterns in git operations?

### 7. Testing
- [ ] Are new functions pure where possible?
- [ ] Are side effects isolated and mockable?
- [ ] Is the change testable without real git/AI dependencies?

## 🎯 Scoring Rubric (for AI review output)

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Correctness | 3.0 | No logic bugs, edge cases handled |
| Security | 2.0 | No vulnerabilities, secrets exposed |
| Performance | 1.5 | Efficient, no wasted resources |
| Code Quality | 2.0 | Readable, well-named, structured |
| Maintainability | 1.5 | Extensible, testable, documented |

**Formula:** `total = Σ(score × weight) / 10`
