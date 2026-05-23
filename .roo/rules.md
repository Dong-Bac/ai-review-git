# ai-review-py — Project Rules

> AI-powered Git code review CLI tool (Python 3.11+)

---

## 🏗️ Architecture & Code Organization

- **CLI entry** → [`src/index.py`](src/index.py:1) — Typer app, no business logic
- **Orchestrator** → [`src/commands/review.py`](src/commands/review.py:1) — coordinates workflow
- **Types** → [`src/types.py`](src/types.py:1) — all dataclass definitions
- **Config** → [`src/config.py`](src/config.py:1) — env-based config loader
- **AI** → [`src/ai/`](src/ai/) — provider abstraction + prompt builder
- **Git** → [`src/git/`](src/git/) — async GitPython wrappers
- **Cache** → [`src/cache.py`](src/cache.py:1) + [`src/cache_backend.py`](src/cache_backend.py:1)
- **Rules** → [`src/rules/__init__.py`](src/rules/__init__.py:1) — loads `.roo/rules.md`
- **Utils** → [`src/utils/`](src/utils/) — file I/O, terminal, logging

## 📐 Coding Standards

| Rule | Convention |
|------|-----------|
| Python version | 3.11+ (use `X \| Y` unions, `match/case`, `str.removeprefix`) |
| Naming | `snake_case` for functions/vars, `PascalCase` for classes, `UPPER_CASE` for constants |
| Paths | Prefer `pathlib.Path` over `os.path` |
| Strings | Use f-strings, never `.format()` or `%` |
| Types | All functions MUST have complete type annotations |
| Data structures | Use `dataclass` or Pydantic, never plain dicts |
| Async | Consistent `async`/`await` — no mixing sync I/O in async context |
| Error handling | Always handle exceptions, never `except: pass` silently |

## 🔒 Security Rules

- Never hardcode secrets, API keys, or credentials
- Validate all external inputs (env vars, CLI args, file paths)
- Use `httpx` with explicit timeouts (120s for AI calls)
- No `eval()`, `exec()`, or unsafe deserialization
- Sanitize file paths to prevent path traversal

## ⚡ Performance

- Use `asyncio.gather()` for concurrent file reads
- Cache AI responses by git diff hash (SHA-256)
- Truncate large file contents before sending to AI (12K diff, 6K per file)
- Avoid N+1 patterns in git operations

## 🧪 Testing

- Pure functions preferred — no side effects
- Mock git, file I/O, and AI provider in tests
- Use `pytest` + `pytest-asyncio`
- Test cache, prompt builder, config loader, git utils

## 📁 File Reference

| File | Purpose |
|------|---------|
| [`src/index.py`](src/index.py:1) | CLI entry point — Typer app |
| [`src/types.py`](src/types.py:1) | Core domain types (dataclasses) |
| [`src/config.py`](src/config.py:1) | Environment config loader |
| [`src/commands/review.py`](src/commands/review.py:1) | Review orchestrator |
| [`src/ai/__init__.py`](src/ai/__init__.py:1) | Provider factory |
| [`src/ai/providers.py`](src/ai/providers.py:1) | AIProvider ABC + DeepSeek + OpenRouter |
| [`src/ai/prompt_builder.py`](src/ai/prompt_builder.py:1) | System + user prompt assembly |
| [`src/git/index.py`](src/git/index.py:1) | Git diff, staged files, branch |
| [`src/cache.py`](src/cache.py:1) | ReviewCache (memory + optional SQLite) |
| [`src/cache_backend.py`](src/cache_backend.py:1) | CacheBackend ABC + MemoryCache + SQLiteCache |
| [`src/rules/__init__.py`](src/rules/__init__.py:1) | Load `.roo/rules.md` or defaults |
| [`src/utils/files.py`](src/utils/files.py:1) | Async file reading + truncation |
| [`src/utils/terminal.py`](src/utils/terminal.py:1) | Rich terminal output |
| [`src/utils/logger.py`](src/utils/logger.py:1) | Structured logging setup |
| [`pyproject.toml`](pyproject.toml:1) | Project metadata + dependencies |
| [`.env.example`](.env.example:1) | Environment variable template |

## 🔄 Workflow

```
git add <files>  →  ai-review review
                      ├── Check git repo
                      ├── Read staged diff + files
                      ├── Load .roo/rules.md
                      ├── Build prompt (system + user)
                      ├── Check cache (SHA-256 of diff)
                      ├── Call AI provider (streaming)
                      └── Display + cache result
```

## 🚫 What NOT To Do

- Don't put business logic in CLI entry points
- Don't use `print()` in production code (use Rich or logging)
- Don't modify `.roo/rules.md` programmatically — it's user-editable
- Don't expose API keys in error messages or logs
- Don't add sync I/O in async functions
