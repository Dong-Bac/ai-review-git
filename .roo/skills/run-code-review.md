# Skill: Run Code Review

> Performs a complete code review of the project using the built-in AI review tool.

## Trigger

When user says: "review the code" or "run code review" or "analyze the project"

## Steps

### 1. Read Context
- [`.roo/hooks/pre-review.md`](../hooks/pre-review.md) — Review checklist
- [`.roo/memory/architecture.md`](../memory/architecture.md) — Architecture reference
- [`.roo/memory/decisions.md`](../memory/decisions.md) — Design decisions

### 2. Run the Review Tool

```bash
ai-review review
```

Or with options:

```bash
# With verbose logging
ai-review review --verbose

# Bypass cache
ai-review review --no-cache

# Use persistent cache
ai-review review --persistent-cache

# Longer cache TTL
ai-review review --cache-ttl 600
```

### 3. Analyze Results

- Check scoring rubric (5 criteria × weights)
- Review severity levels (🔴 Critical → 🔵 Info)
- Verify file:line references are accurate
- Check for false positives

### 4. Manual Review Areas

If the tool cannot be run (e.g., no API key), perform manual review using:

- [`.roo/hooks/pre-review.md`](../hooks/pre-review.md) checklist
- [`src/`](../../src/) source code analysis
- [`plans/`](../../plans/) for known issues and improvement plans
