# System Architecture — ai-review-py

> Complete architecture documentation for the AI-powered Git code review CLI.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI (Typer)                          │
│                     src/index.py:1                          │
│                                                             │
│  ai-review review [--use-env] [--verbose] [--no-cache]      │
│                    [--cache-ttl] [--persistent-cache]       │
└───────────────────────┬─────────────────────────────────────┘
                        │ asyncio.run()
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Review Orchestrator                        │
│                  src/commands/review.py:1                    │
│                                                             │
│  1. Init cache (memory ± SQLite)                            │
│  2. Load config (env vars)                                  │
│  3. Verify git repository                                   │
│  4. Read staged diff + changed files                        │
│  5. Read file contents (async concurrent)                   │
│  6. Load .roo/rules.md                                      │
│  7. Build ReviewContext + Prompt                            │
│  8. Check cache (SHA-256 of diff)                           │
│  9. Call AI provider (streaming)                            │
│ 10. Display result + store in cache                         │
└───┬───────┬───────┬───────┬───────┬───────┬───────┬─────────┘
    │       │       │       │       │       │       │
    ▼       ▼       ▼       ▼       ▼       ▼       ▼
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────────┐
│ Git │ │File │ │Rules│ │Cache│ │ AI  │ │Term │ │ Logger  │
│     │ │ I/O │ │     │ │     │ │     │ │inal │ │         │
└─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────────┘
```

## 📦 Module Responsibilities

### [`src/index.py`](../../src/index.py:1) — CLI Entry Point
- Typer application definition
- Global options: `--use-env`, `--verbose`, `--no-cache`, `--cache-ttl`, `--persistent-cache`
- No business logic — delegates to command handlers via `asyncio.run()`

### [`src/types.py`](../../src/types.py:1) — Domain Types
All data structures as dataclasses:

| Type | Fields | Purpose |
|------|--------|---------|
| `ChangedFile` | `path`, `status`, `content` | A file in the changeset |
| `GitDiffInfo` | `diff`, `changed_files`, `branch`, `is_empty` | Parsed git state |
| `ProjectInfo` | `name`, `root_path` | Project metadata |
| `ReviewContext` | `diff`, `changed_files`, `branch`, `rules`, `project_info` | Full context for AI |
| `Prompt` | `system`, `user` | Prepared AI prompt |
| `ReviewScore` | `correctness`, `security`, `performance`, `quality`, `maintainability` | Scoring breakdown |
| `ReviewResult` | `content`, `model`, `tokens_used`, `score` | AI response |
| `AppConfig` | `api_key`, `model`, `base_url`, `app_name`, `app_url`, `max_tokens`, `provider` | Runtime config |
| `StreamChunk` | `content`, `finish_reason` | Streaming response chunk |

### [`src/config.py`](../../src/config.py:1) — Configuration
- Loads `.env` from CWD (or `--use-env` loads from project root)
- Returns `AppConfig` dataclass
- Validates `DEEPSEEK_API_KEY` is present (fail-fast)
- Supports provider selection via `PROVIDER` env var

### [`src/commands/review.py`](../../src/commands/review.py:1) — Orchestrator
- Coordinates the full review workflow
- Uses Rich `Progress` for status indicators
- Handles error states with `SystemExit(1)`
- Implements cache-first strategy

### [`src/ai/__init__.py`](../../src/ai/__init__.py:1) — Provider Factory
- Maps `config.provider` string to provider class
- Currently supports: `deepseek`, `openrouter`
- Returns `AIProvider` instance

### [`src/ai/providers.py`](../../src/ai/providers.py:1) — AI Providers
- `AIProvider` — Abstract base class (ABC)
- `DeepSeekProvider` — DeepSeek API implementation
- `OpenRouterProvider` — OpenRouter API implementation
- Both support `ask()` (non-streaming) and `stream()` (SSE streaming)
- Both use `@retry` with exponential backoff (3 attempts)
- Both use `httpx.AsyncClient` with 120s timeout

### [`src/ai/prompt_builder.py`](../../src/ai/prompt_builder.py:1) — Prompt Assembly
- `build_prompt(ctx)` → `Prompt(system, user)`
- System prompt: role definition + project rules + scoring rubric + severity levels + output format
- User prompt: project context + commit context + changed files + git diff + file contents + review instructions
- Content truncation: 12K chars for diff, 6K chars per file

### [`src/git/index.py`](../../src/git/index.py:1) — Git Operations
- `is_git_repository()` — Check if CWD is in a git repo
- `get_current_branch()` — Get active branch name
- `get_staged_diff()` — Get `git diff --cached` output
- `get_staged_files()` — Get changed files with status (A/M/D/R)
- `get_git_diff_info()` — High-level: gather all git info concurrently
- All operations use `asyncio.to_thread()` for non-blocking execution

### [`src/cache.py`](../../src/cache.py:1) + [`src/cache_backend.py`](../../src/cache_backend.py:1) — Caching
- `ReviewCache` — Two-tier cache (memory → persistent)
- `CacheBackend` — Abstract interface
- `MemoryCache` — In-memory dict with TTL
- `SQLiteCache` — Persistent SQLite with TTL cleanup
- Cache key: SHA-256 hash of git diff string
- Default TTL: 300 seconds

### [`src/rules/__init__.py`](../../src/rules/__init__.py:1) — Rules Loading
- Loads `.roo/rules.md` from project root
- Falls back to `DEFAULT_RULES` (5 categories × 4-5 rules each)
- Used in system prompt construction

### [`src/utils/files.py`](../../src/utils/files.py:1) — File I/O
- `read_file_safe()` — Async file read with error handling
- `read_files_concurrently()` — Parallel file reads via `asyncio.gather`
- `truncate_content()` — Smart truncation at line boundaries
- `resolve_project_name()` — Read from `package.json` or `pyproject.toml`

### [`src/utils/terminal.py`](../../src/utils/terminal.py:1) — Terminal UI
- Rich-based console output
- `info()`, `success()`, `warn()`, `error()` — Status messages
- `print_review()` — Rendered Markdown in panel
- `stream_review()` — Live streaming output
- UTF-8 forced on Windows for Vietnamese/Unicode support

### [`src/utils/logger.py`](../../src/utils/logger.py:1) — Logging
- RichHandler for console (stderr)
- File handler at `~/.ai_review/logs/ai-review-YYYY-MM-DD.log`
- Default level: WARNING (DEBUG with `--verbose`)
- Auto-cleanup logs older than 7 days

## 🔄 Data Flow

```
User runs: ai-review review
  │
  ├─ [1] ReviewCache initialized (memory ± SQLite)
  ├─ [2] load_config() → AppConfig
  ├─ [3] is_git_repository() → bool
  ├─ [4] get_git_diff_info() → GitDiffInfo
  │       ├─ get_staged_diff() → str (diff)
  │       ├─ get_staged_files() → list[ChangedFile]
  │       └─ get_current_branch() → str
  ├─ [5] read_files_concurrently() → dict[path, content]
  ├─ [6] load_rules() → str (rules.md or defaults)
  ├─ [7] build_prompt(ReviewContext) → Prompt
  │       ├─ _build_system_prompt(rules) → str
  │       └─ _build_user_prompt(ctx) → str
  ├─ [8] cache.get(SHA256(diff)) → ReviewResult | None
  ├─ [9] create_ai_provider(config) → AIProvider
  │       └─ provider.stream(prompt) → AsyncIterator[StreamChunk]
  ├─ [10] stream_review(chunk) → terminal output
  └─ [11] cache.set(key, result) → stored
```

## 🧩 Extension Points

| Extension | How | File |
|-----------|-----|------|
| New AI provider | Subclass `AIProvider`, register in factory | [`src/ai/providers.py`](../../src/ai/providers.py:1) |
| New CLI command | Create handler, add `@app.command()` | [`src/index.py`](../../src/index.py:1) |
| New cache backend | Implement `CacheBackend`, wire into `ReviewCache` | [`src/cache_backend.py`](../../src/cache_backend.py:1) |
| Custom rules | Edit `.roo/rules.md` in project root | [`.roo/rules.md`](../rules.md) |
| Output format | Modify `print_review()` / `stream_review()` | [`src/utils/terminal.py`](../../src/utils/terminal.py:1) |
