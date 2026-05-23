# Skill: Add New AI Provider

> Adds a new AI provider (e.g., OpenAI, Anthropic, Gemini) to the project.

## Trigger

When user says: "add support for [provider name]" or "add new AI provider"

## Steps

### 1. Read Reference Files
- [`.roo/memory/architecture.md`](../memory/architecture.md) — Understand provider architecture
- [`.roo/templates/new-provider.md`](../templates/new-provider.md) — Follow template
- [`src/ai/providers.py`](../../src/ai/providers.py:1) — Existing providers for reference
- [`src/ai/__init__.py`](../../src/ai/__init__.py:1) — Factory registration
- [`src/types.py`](../../src/types.py:1) — Type definitions
- [`src/config.py`](../../src/config.py:1) — Config structure
- [`.env.example`](../../.env.example:1) — Env var template

### 2. Create Provider Class

Add to [`src/ai/providers.py`](../../src/ai/providers.py:1):

```python
class NewProvider(AIProvider):
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def ask(self, prompt: Prompt) -> ReviewResult:
        ...

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def stream(self, prompt: Prompt) -> AsyncIterator[StreamChunk]:
        ...
```

### 3. Register in Factory

Edit [`src/ai/__init__.py`](../../src/ai/__init__.py:1):

```python
from src.ai.providers import NewProvider

provider = {
    ...,
    "newprovider": NewProvider,
}
```

### 4. Update Config (if needed)

- Add new env vars to [`src/config.py`](../../src/config.py:1)
- Update [`.env.example`](../../.env.example:1)

### 5. Verify

- [ ] Provider class extends `AIProvider`
- [ ] Both `ask()` and `stream()` implemented
- [ ] `@retry` decorator applied
- [ ] Registered in factory
- [ ] `.env.example` updated
- [ ] Config loader handles new env vars
