# ai-review (Python)

> AI-powered code review CLI for your git staged changes.

[![CI](https://github.com/your-org/ai-review/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/ai-review/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/ai-review)](https://pypi.org/project/ai-review/)
[![Python Versions](https://img.shields.io/pypi/pyversions/ai-review)](https://pypi.org/project/ai-review/)
[![License](https://img.shields.io/github/license/your-org/ai-review)](LICENSE)

## Features

- 🔍 Reads staged git diff automatically
- 📄 Loads changed file contents for full context
- 🤖 Sends context to AI via DeepSeek
- 🎨 Beautiful terminal output powered by **Rich**
- 📋 Custom project rules via `.roo/rules.md`
- ⚡ Fully async — fast concurrent file reads

## Installation

```bash
cd ai-review-py

# Create virtualenv
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Lightweight install (recommended) — only essential dependencies
pip install -e .

# Full install with vector memory support (~200MB additional)
# Required for --memory flag (similar past review retrieval)
pip install -e ".[memory]"
```

> **Note:** The base install is lightweight (~10MB). The `[memory]` extra adds
> `chromadb` and `sentence-transformers` which pull in heavy packages like
> `torch` (~123MB), `scipy`, `onnxruntime`, etc. Only install if you need
> vector memory features.

## Setup

Create a `.env` file in the directory where you run `ai-review`:

```env
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-chat
```


## Usage

```bash
# Stage your changes first
git add src/feature.py

# Run the review
ai-review review
```

## Custom Rules

Create `.roo/rules.md` in your project root:

```markdown
# My Project Rules
- Use Python 3.11+ syntax
- No print() in production code  
- All async functions must handle exceptions
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `DEEPSEEK_API_KEY` | *(required)* | Your DEEPSEEK API key |
| `DEEPSEEK_MODEL` | `deepseek/deepseek-chat` | Model to use |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | API base URL |
| `AI_MAX_TOKENS` | `4096` | Max tokens in response |

## Architecture

```
src/
├── index.py          # CLI entry (Typer) — no business logic
├── types.py          # Dataclass types
├── config.py         # Env config loader
├── commands/
│   └── review.py     # Review orchestrator
├── git/              # GitPython wrappers (async)
├── ai/
│   ├── providers.py  # AIProvider ABC + DEEPSEEK
│   └── prompt_builder.py
├── rules/            # .roo/rules.md loader
└── utils/
    ├── terminal.py   # Rich UI helpers
    └── files.py      # File reading, truncation
```

## Roadmap

- [ ] Streaming response output
- [ ] Multi-agent review
- [ ] Auto-fix mode
- [ ] Git hooks integration
- [ ] PR review (GitHub / GitLab)
- [ ] RAG + vector memory
- [ ] MCP tools integration
- [ ] Security scanning
- [ ] Patch generation
