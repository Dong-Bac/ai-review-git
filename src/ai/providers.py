"""
AI Provider abstraction + DeepSeek implementation.
Add new providers by subclassing AIProvider.
"""

from __future__ import annotations
from abc import ABC, abstractmethod

import httpx

from src.types import AppConfig, Prompt, ReviewResult


# ── Abstract base (the contract) ─────────────────────────────

class AIProvider(ABC):
    @abstractmethod
    async def ask(self, prompt: Prompt) -> ReviewResult:
        """Send a prompt and return the review result."""
        ...

    # Future:
    # @abstractmethod
    # async def stream(self, prompt: Prompt) -> AsyncIterable[str]: ...


# ── DeepSeek implementation ───────────────────────────────────

class DeepSeekProvider(AIProvider):
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    async def ask(self, prompt: Prompt) -> ReviewResult:
        payload = {
            "model": self._config.model,
            "max_tokens": self._config.max_tokens,
            "messages": [
                {"role": "system", "content": prompt.system},
                {"role": "user",   "content": prompt.user},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._config.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self._config.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
            except httpx.ConnectError as exc:
                raise RuntimeError(
                    f"Network error contacting DeepSeek: {exc}\n"
                    "Check your internet connection."
                ) from exc

        if response.status_code != 200:
            raise RuntimeError(
                f"DeepSeek API error {response.status_code}: "
                f"{response.text[:300]}"
            )

        data = response.json()

        if "error" in data:
            raise RuntimeError(f"DeepSeek returned an error: {data['error']['message']}")

        choices = data.get("choices", [])
        if not choices or not choices[0].get("message", {}).get("content"):
            raise RuntimeError("DeepSeek returned an empty response. Try again.")

        return ReviewResult(
            content=choices[0]["message"]["content"],
            model=data.get("model", self._config.model),
            tokens_used=data.get("usage", {}).get("total_tokens"),
        )

    # ── Future streaming stub ───────────────────────────────
    # async def stream(self, prompt: Prompt) -> AsyncIterable[str]:
    #     payload = {**payload, "stream": True}
    #     async with httpx.AsyncClient() as client:
    #         async with client.stream("POST", url, ...) as r:
    #             async for line in r.aiter_lines():
    #                 yield parse_sse(line)
