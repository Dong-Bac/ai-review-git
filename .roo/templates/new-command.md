# New CLI Command Template

> Template for adding a new command to [`src/index.py`](../../src/index.py:1).

## Steps

### 1. Create Command Module

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

### 2. Register in CLI

Edit [`src/index.py`](../../src/index.py:1):

```python
@app.command()
def <name>(
    # Add CLI options here
) -> None:
    """<Description of the command>"""
    from src.commands.<name> import run_<name>
    asyncio.run(run_<name>())
```

### 3. Export from Package

Edit [`src/commands/__init__.py`](../../src/commands/__init__.py:1):

```python
from src.commands.<name> import run_<name>

__all__ = ["run_<name>"]
```

## Command Patterns

| Pattern | Example |
|---------|---------|
| Simple flag | `verbose: bool = typer.Option(False, "--verbose")` |
| Value option | `name: str = typer.Option("default", "--name")` |
| Argument | `path: str = typer.Argument(..., help="Path")` |

## Checklist

- [ ] Command module created in `src/commands/`
- [ ] Registered with `@app.command()` in [`src/index.py`](../../src/index.py:1)
- [ ] Exported from [`src/commands/__init__.py`](../../src/commands/__init__.py:1)
- [ ] Uses `asyncio.run()` for async execution
- [ ] Error handling with `SystemExit(1)` for fatal errors
- [ ] Uses Rich for terminal output (not `print()`)
- [ ] Respects `--verbose` flag for logging
