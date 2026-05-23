# Pre-Read Hook — Context Loader

> Automatically loaded before any code generation or modification task.
> Provides essential project context to ensure AI understands the full architecture.

## 📋 Required Reading

Before writing any code, ALWAYS read these files in order:

### 1. Core Architecture
- [`.roo/memory/architecture.md`](../memory/architecture.md) — System architecture, data flow, module responsibilities
- [`.roo/memory/decisions.md`](../memory/decisions.md) — Key architectural decisions and rationale

### 2. Current State
- [`src/types.py`](../../src/types.py:1) — All dataclass definitions (must understand before modifying any type)
- [`src/config.py`](../../src/config.py:1) — Config structure and env vars
- [`src/index.py`](../../src/index.py:1) — CLI entry point and available commands

### 3. Target Module
Read the specific module(s) you're about to modify:

| If modifying | Also read |
|-------------|-----------|
| [`src/ai/providers.py`](../../src/ai/providers.py:1) | [`src/ai/__init__.py`](../../src/ai/__init__.py:1) |
| [`src/ai/prompt_builder.py`](../../src/ai/prompt_builder.py:1) | [`src/rules/__init__.py`](../../src/rules/__init__.py:1) |
| [`src/commands/review.py`](../../src/commands/review.py:1) | All files in `src/` |
| [`src/cache.py`](../../src/cache.py:1) | [`src/cache_backend.py`](../../src/cache_backend.py:1) |
| [`src/git/index.py`](../../src/git/index.py:1) | — |
| [`src/utils/files.py`](../../src/utils/files.py:1) | — |
| [`src/utils/terminal.py`](../../src/utils/terminal.py:1) | — |

## 🔍 Pre-Code Checklist

Before writing/modifying code, verify:

- [ ] I understand the full data flow (CLI → git → prompt → AI → display)
- [ ] I've checked existing types in [`src/types.py`](../../src/types.py:1)
- [ ] I've checked the config schema in [`src/config.py`](../../src/config.py:1)
- [ ] I understand the cache layer (memory + optional SQLite)
- [ ] I know which AI providers are supported (DeepSeek, OpenRouter)
- [ ] I've checked `.roo/rules.md` for project-specific rules
- [ ] I've checked `.roo/memory/` for architectural decisions

## ⚠️ Common Pitfalls

1. **Don't break the provider factory** — [`src/ai/__init__.py`](../../src/ai/__init__.py:1) dispatches by `config.provider`
2. **Don't bypass cache** — Always use `ReviewCache` unless `--no-cache` is set
3. **Don't hardcode limits** — Use `AppConfig` or constants, not magic numbers
4. **Don't forget async** — All I/O operations must use `asyncio.to_thread` or async libs
5. **Don't break streaming** — The `stream()` method is the primary UX path
