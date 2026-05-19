# Project Review Rules

## Language & Style
- This project uses Python 3.11+ — use modern syntax (match/case, `X | Y` unions, etc.)
- Follow PEP 8 naming: `snake_case` for functions/vars, `PascalCase` for classes
- Prefer `pathlib.Path` over `os.path`
- Use f-strings, not `.format()` or `%`

## Security
- Never allow secrets, API keys, or credentials in code
- Validate all external inputs
- Use `httpx` with timeouts set

## Architecture
- Keep business logic out of CLI entry points
- Async functions should use `await` consistently — no mixing sync I/O in async context
- Use dataclasses or Pydantic for data structures, not plain dicts

## Testing
- New utilities should be pure functions with no side effects
- Avoid global mutable state
