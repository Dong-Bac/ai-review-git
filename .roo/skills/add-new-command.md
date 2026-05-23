# Skill: Add New CLI Command

> Adds a new command (e.g., `ai-review init`, `ai-review config`, `ai-review version`).

## Trigger

When user says: "add a [name] command" or "create new command"

## Steps

### 1. Read Reference Files
- [`.roo/templates/new-command.md`](../templates/new-command.md) — Follow template
- [`src/index.py`](../../src/index.py:1) — Existing commands for reference
- [`src/commands/review.py`](../../src/commands/review.py:1) — Existing command handler

### 2. Create Command Module

Create `src/commands/<name>.py`:

```python
"""
`ai-review <name>` command handler.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

async def run_<name>(**kwargs) -> None:
    """Implement <name> command logic."""
    ...
```

### 3. Register in CLI

Edit [`src/index.py`](../../src/index.py:1):

```python
@app.command()
def <name>(
    # options...
) -> None:
    """<Description>"""
    from src.commands.<name> import run_<name>
    asyncio.run(run_<name>())
```

### 4. Export from Package

Edit [`src/commands/__init__.py`](../../src/commands/__init__.py:1):

```python
from src.commands.<name> import run_<name>
__all__ = [...]
```

### 5. Verify

- [ ] Command module created in `src/commands/`
- [ ] Registered with `@app.command()` in [`src/index.py`](../../src/index.py:1)
- [ ] Exported from [`src/commands/__init__.py`](../../src/commands/__init__.py:1)
- [ ] Uses `asyncio.run()` for async execution
- [ ] Error handling with `SystemExit(1)` for fatal errors
- [ ] Uses Rich for terminal output
- [ ] Respects `--verbose` flag
