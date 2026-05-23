# Skill: Refactor a Module

> Refactors a specific module following project patterns and best practices.

## Trigger

When user says: "refactor [module]" or "improve [module]" or "clean up [module]"

## Steps

### 1. Read Context
- [`.roo/hooks/pre-read.md`](../hooks/pre-read.md) — Pre-read checklist
- [`.roo/memory/architecture.md`](../memory/architecture.md) — Architecture reference
- [`.roo/memory/decisions.md`](../memory/decisions.md) — Design decisions
- [`.roo/rules.md`](../rules.md) — Project rules

### 2. Read Target Module

Read the full source of the module to refactor.

### 3. Identify Issues

Check for:
- [ ] Missing type annotations
- [ ] Sync I/O in async functions
- [ ] Magic numbers (hardcoded constants)
- [ ] Duplicate code
- [ ] Missing error handling
- [ ] Violations of SRP (Single Responsibility Principle)
- [ ] Missing docstrings
- [ ] Inconsistent naming

### 4. Apply Changes

Follow project patterns:
- Use dataclasses from [`src/types.py`](../../src/types.py:1)
- Use `asyncio.to_thread()` for blocking operations
- Use Rich for terminal output
- Use logging instead of print
- Add type hints to all functions

### 5. Verify

- [ ] Module still imports correctly
- [ ] Type annotations complete
- [ ] No sync I/O in async functions
- [ ] Constants extracted (no magic numbers)
- [ ] Error handling added
- [ ] Docstrings for public functions
