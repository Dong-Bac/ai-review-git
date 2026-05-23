# Architectural Decision Records (ADR)

> Key architectural decisions for ai-review-py.

---

## ADR-001: Async-First Design

**Status:** Accepted  
**Context:** The tool reads git diffs, multiple files, and calls external APIs. Synchronous I/O would block the CLI.  
**Decision:** Use `asyncio` throughout. All I/O operations use `asyncio.to_thread()` or native async libraries (`httpx`, `aiosqlite`).  
**Consequences:**
- + Concurrent file reads via `asyncio.gather()`
- + Non-blocking HTTP calls to AI providers
- - Requires `asyncio.run()` wrapper in CLI entry points

## ADR-002: Dataclasses over Dicts

**Status:** Accepted  
**Context:** Need type-safe, immutable data structures for domain objects.  
**Decision:** Use Python `dataclass` for all domain types in [`src/types.py`](../../src/types.py:1).  
**Consequences:**
- + Type hints work naturally
- + IDE autocompletion
- + No runtime validation overhead (vs Pydantic)
- - Manual validation in config loader

## ADR-003: Provider Factory Pattern

**Status:** Accepted  
**Context:** Support multiple AI providers (DeepSeek, OpenRouter, future OpenAI/Anthropic).  
**Decision:** Abstract base class `AIProvider` with factory in [`src/ai/__init__.py`](../../src/ai/__init__.py:1).  
**Consequences:**
- + Easy to add new providers
- + Consistent interface (`ask()` + `stream()`)
- - Duplicate code between providers (mitigated by base class)

## ADR-004: Two-Tier Cache

**Status:** Accepted  
**Context:** Cache AI responses to save tokens and time. Need fast in-memory cache + optional persistence.  
**Decision:** `ReviewCache` wraps `MemoryCache` (primary) + optional `SQLiteCache` (secondary).  
**Consequences:**
- + Fast reads from memory
- + Survives restarts with SQLite
- + Clean abstraction via `CacheBackend` interface
- - Two code paths to maintain

## ADR-005: Vietnamese Language for AI Prompts

**Status:** Accepted  
**Context:** Target users are Vietnamese-speaking developers.  
**Decision:** System prompt and review instructions in Vietnamese. Code comments in English.  
**Consequences:**
- + Better comprehension for target users
- - Non-Vietnamese contributors need translation

## ADR-006: SHA-256 Cache Key

**Status:** Accepted  
**Context:** Need deterministic cache key from git diff content.  
**Decision:** Use `hashlib.sha256(diff.encode("utf-8")).hexdigest()`.  
**Consequences:**
- + Deterministic (same diff → same key)
- + No false collisions
- - Key changes on whitespace diffs (acceptable)

## ADR-007: Content Truncation Strategy

**Status:** Accepted  
**Context:** Large files exceed AI context windows. Need smart truncation.  
**Decision:** Truncate at line boundaries with clear marker. Diff: 12K chars, per-file: 6K chars.  
**Consequences:**
- + Prevents broken code blocks in prompts
- + AI knows content was truncated
- - May lose context from truncated sections

## ADR-008: Rich for Terminal UI

**Status:** Accepted  
**Context:** Need beautiful, structured terminal output with Markdown rendering.  
**Decision:** Use Rich library for all terminal output.  
**Consequences:**
- + Markdown rendering in terminal
- + Progress spinners, panels, colored output
- + Unicode/Vietnamese support with UTF-8 override

## ADR-009: GitPython over Subprocess

**Status:** Accepted  
**Context:** Need to interact with git repository.  
**Decision:** Use `GitPython` library instead of `subprocess` calls.  
**Consequences:**
- + Higher-level API
- + Automatic repo discovery
- + Type-safe git operations
- - Additional dependency

## ADR-010: Retry with Exponential Backoff

**Status:** Accepted  
**Context:** AI APIs can be rate-limited or temporarily unavailable.  
**Decision:** Use `tenacity` with `@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))`.  
**Consequences:**
- + Resilient to transient failures
- + No manual retry logic
- - Delays failure by ~20s max (acceptable)

## ADR-011: Scoring Rubric in System Prompt

**Status:** Accepted  
**Context:** Need structured, quantifiable code reviews.  
**Decision:** Embed scoring rubric (5 criteria × weights) directly in system prompt.  
**Consequences:**
- + AI produces structured output
- + Consistent scoring across reviews
- + Users understand evaluation criteria
