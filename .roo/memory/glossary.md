# Project Glossary

> Domain-specific terms and abbreviations used in ai-review-py.

---

## Core Concepts

| Term | Definition | Location |
|------|------------|----------|
| **Changeset** | Set of staged file changes to be reviewed | [`src/types.py`](../../src/types.py:1) `GitDiffInfo` |
| **Staged diff** | Output of `git diff --cached` — changes staged for commit | [`src/git/index.py`](../../src/git/index.py:44) |
| **Review context** | Complete context sent to AI: diff + files + rules + project info | [`src/types.py`](../../src/types.py:1) `ReviewContext` |
| **Prompt** | System + user message pair sent to AI provider | [`src/types.py`](../../src/types.py:1) `Prompt` |
| **Streaming** | Real-time output of AI response via Server-Sent Events | [`src/ai/providers.py`](../../src/ai/providers.py:98) |
| **Scoring rubric** | 5-criterion weighted scoring system (0-10 scale) | [`src/ai/prompt_builder.py`](../../src/ai/prompt_builder.py:21) |
| **Severity level** | Classification of issues: Critical/Major/Minor/Info | [`src/ai/prompt_builder.py`](../../src/ai/prompt_builder.py:36) |

## Code Components

| Term | Definition | File |
|------|------------|------|
| **Typer app** | CLI framework entry point | [`src/index.py`](../../src/index.py:1) |
| **Orchestrator** | Coordinates the review workflow | [`src/commands/review.py`](../../src/commands/review.py:1) |
| **Provider** | AI service implementation (DeepSeek, OpenRouter) | [`src/ai/providers.py`](../../src/ai/providers.py:1) |
| **Provider factory** | Maps provider name → provider class | [`src/ai/__init__.py`](../../src/ai/__init__.py:1) |
| **Prompt builder** | Assembles system + user prompts from context | [`src/ai/prompt_builder.py`](../../src/ai/prompt_builder.py:1) |
| **Cache backend** | Storage implementation for cached reviews | [`src/cache_backend.py`](../../src/cache_backend.py:1) |
| **Review cache** | Two-tier cache (memory + optional persistent) | [`src/cache.py`](../../src/cache.py:1) |
| **Rules loader** | Loads `.roo/rules.md` or returns defaults | [`src/rules/__init__.py`](../../src/rules/__init__.py:1) |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DEEPSEEK_API_KEY` | *(required)* | API key for authentication |
| `DEEPSEEK_MODEL` | `deepseek-chat` | Model identifier |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | API base URL |
| `AI_MAX_TOKENS` | `8192` | Max tokens in AI response |
| `PROVIDER` | `deepseek` | AI provider selection |
| `APP_NAME` | `ai-review` | App name for API headers |
| `APP_URL` | *(optional)* | App URL for API headers |

## CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--use-env` | `False` | Load `.env` from project dir instead of CWD |
| `--verbose` / `-v` | `False` | Enable DEBUG logging |
| `--no-cache` | `False` | Bypass cache, force fresh AI call |
| `--cache-ttl` | `300` | Cache TTL in seconds |
| `--persistent-cache` | `False` | Use SQLite persistent cache |

## File Status Types

| Status | Meaning |
|--------|---------|
| `added` | New file staged |
| `modified` | Existing file changed |
| `deleted` | File removed |
| `renamed` | File renamed |
| `unknown` | Unrecognized status |

## Scoring Criteria

| Criterion | Weight | Focus |
|-----------|--------|-------|
| Correctness | 3.0 | Logic bugs, edge cases, type safety |
| Security | 2.0 | Vulnerabilities, secrets, injection |
| Performance | 1.5 | Efficiency, resource usage, N+1 |
| Code Quality | 2.0 | Readability, naming, structure, DRY |
| Maintainability | 1.5 | Extensibility, testability, docs |

## Severity Levels

| Level | Emoji | Meaning |
|-------|-------|---------|
| Critical | 🔴 | Crash, data loss, security vulnerability |
| Major | 🟠 | Logic error, severe performance issue |
| Minor | 🟡 | Convention violation, readability |
| Info | 🔵 | Suggestion, best practice tip |
