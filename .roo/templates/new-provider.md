# New AI Provider Template

> Template for adding a new AI provider to [`src/ai/providers.py`](../../src/ai/providers.py:1).

## Steps

### 1. Create Provider Class

```python
class NewProvider(AIProvider):
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def ask(self, prompt: Prompt) -> ReviewResult:
        # Implement non-streaming request
        ...

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def stream(self, prompt: Prompt) -> AsyncIterator[StreamChunk]:
        # Implement streaming request
        ...
```

### 2. Register in Factory

Edit [`src/ai/__init__.py`](../../src/ai/__init__.py:1):

```python
from src.ai.providers import NewProvider

provider = {
    "deepseek": DeepSeekProvider,
    "openrouter": OpenRouterProvider,
    "newprovider": NewProvider,  # ← ADD
}
```

### 3. Add Config (if needed)

Edit [`src/config.py`](../../src/config.py:1) and [`.env.example`](../../.env.example:1) if the provider needs custom env vars.

### 4. Update Types (if needed)

Edit [`src/types.py`](../../src/types.py:1) if the provider returns different metadata.

## Required Interface

```python
class AIProvider(ABC):
    @abstractmethod
    async def ask(self, prompt: Prompt) -> ReviewResult: ...

    @abstractmethod
    async def stream(self, prompt: Prompt) -> AsyncIterator[StreamChunk]: ...
```

## Checklist

- [ ] Class extends `AIProvider` ABC
- [ ] `@retry` decorator applied to both methods
- [ ] `httpx.AsyncClient` with `timeout=120.0`
- [ ] Proper error handling (RequestError, status codes)
- [ ] Streaming uses SSE format (`data: {...}`)
- [ ] Registered in provider factory
- [ ] Added to `.env.example` if new env vars needed
