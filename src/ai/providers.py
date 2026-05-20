"""
AI Provider abstraction + DeepSeek implementation.
Add new providers by subclassing AIProvider.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import AsyncIterator
import httpx


from src.types import AppConfig, Prompt, ReviewResult, StreamChunk


# ── Abstract base (the contract) ─────────────────────────────
class AIProvider(ABC):
    @abstractmethod
    async def ask(self, prompt: Prompt) -> ReviewResult:
        pass

    @abstractmethod
    async def stream(self, prompt: Prompt) -> AsyncIterator[StreamChunk]:
        pass

    # Future:
    # @abstractmethod
    # async def stream(self, prompt: Prompt) -> AsyncIterable[str]: ...


# ── DeepSeek implementation ───────────────────────────────────

class DeepSeekProvider(AIProvider):
    def __init__ (self, config: AppConfig) -> None:
        self.config = config

    @retry(
            stop = stop_after_attempt(3),
            wait= wait_exponential(
                multiplier=1, min=2, max=10
            )
    )
    async def ask(self, prompt: Prompt) -> ReviewResult:
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": prompt.system},
                {"role": "user", "content": prompt.user},
            ],
            "max_tokens": self.config.max_tokens
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.config.base_url}/v1/chat/completions"

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    url,
                    json = payload,
                    headers = headers,
                )
            except httpx.RequestError as exc:
                raise RuntimeError(
                 f"Error: {exc} \n" 
                 "Please check your network and api"   
                )
            
            if response.status_code != 200:
                raise RuntimeError(
                    f"Api error: {response.status_code} - {response.text}"
                )
            
            if response.status_code ==  429:
                raise RuntimeError("Rate limit exceeded.")

            data = response.json()

            return ReviewResult(
                content = data["choices"][0]["message"]["content"],
                model = data.get("model", "unknown"),
                tokens_used=data.get("usage", {}).get("total_tokens"),
            )

    async def stream(self, prompt: Prompt) -> AsyncIterator[StreamChunk]:
        payload = {
            "model": self.config.model,
            "messages": [
                 {"role": "system", "content": prompt.system},
                {"role": "user", "content": prompt.user},
            ],
            "max_tokens": self.config.max_tokens,
            "stream": True
        }
        headers = {
        "Authorization": f"Bearer {self.config.api_key}",
        "Content-Type": "application/json",
        }
        url = f"{self.config.base_url}/v1/chat/completions"

        async with httpx.AsyncClient(timeout= 120.0) as client:
            try:
                async with client.stream("POST", url, json = payload,
                                         headers = headers) as response:
                    if response.status_code != 200:
                         error_text = await response.aread()
                         raise RuntimeError(f"Api error: {response.status_code} - {error_text}")
                    
                    async for line in response.aiter_lines():
                        if line:
                            if not line.startswith("data: "):
                                continue
                            data_str = line.removeprefix("data: ").strip()
                            if data_str == "[DONE]":
                                break
                            import json
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            finish_reason = data["choices"][0].get("finish_reason")
                            if content or finish_reason:
                                yield StreamChunk(content=content, finish_reason=finish_reason)

            except httpx.RequestError as exc:
                raise RuntimeError(
                 f"Error: {exc} \n" 
                 "Please check your network and api"   
                )

# Chưa sửa:
class OpenRouterProvider(AIProvider):
    def __init__ (self, config: AppConfig) -> None:
        self.config = config

    async def ask(self, prompt: Prompt) -> ReviewResult:
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": prompt.system},
                {"role": "user", "content": prompt.user},
            ],
            "max_tokens": self.config.max_tokens
        }

        headers = {
        "Authorization": f"Bearer {self.config.api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/your-repo",
        "X-Title": "ai-review-py",
    }

        url = f"{self.config.base_url}/v1/chat/completions"

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    url,
                    json = payload,
                    headers = headers,
                )
            except httpx.RequestError as exc:
                raise RuntimeError(
                 f"Error: {exc} \n" 
                 "Please check your network and api"   
                )
            
            if response.status_code != 200:
                raise RuntimeError(
                    f"Api error: {response.status_code} - {response.text}"
                )
            data = response.json()

            return ReviewResult(
                content = data["choices"][0]["message"]["content"],
                model = data.get("model", "unknown"),
                tokens_used=data.get("usage", {}).get("total_tokens"),
            )

    async def stream(self, prompt: Prompt) -> AsyncIterator[StreamChunk]:
        payload = {
        "model": self.config.model,
        "messages": [
            {"role": "system", "content": prompt.system},
            {"role": "user", "content": prompt.user},
        ],
        "max_tokens": self.config.max_tokens,
        "stream": True,
        }
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",
            "X-Title": "ai-review-py",
        }
        url = f"{self.config.base_url}/v1/chat/completions"

        async with httpx.AsyncClient(timeout = 120.0) as client:
            try:
                async with client.stream("POST",
                                         url,
                                         json = payload,
                                         headers= headers) as response:
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        raise RuntimeError(f"Api error: {response.status_code} - {error_text}")
                    
                    async for line in response.aiter_lines():
                        if line:
                            if not line.startswith("data: "):
                                continue
                            data_str = line.removeprefix("data: ").strip()
                            if data_str == "[DONE]":
                                break
                            import json
                            data = json.loads(data_str)
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            finish_reason = data["choices"][0].get("finish_reason")
                            if content or finish_reason:
                                yield StreamChunk(content=content, finish_reason=finish_reason)
            except httpx.RequestError as exc:
                raise RuntimeError(
                 f"Error: {exc} \n" 
                 "Please check your network and api"   
                )

        

    # ── Future streaming stub ───────────────────────────────
    # async def stream(self, prompt: Prompt) -> AsyncIterable[str]:
    #     payload = {**payload, "stream": True}
    #     async with httpx.AsyncClient() as client:
    #         async with client.stream("POST", url, ...) as r:
    #             async for line in r.aiter_lines():
    #                 yield parse_sse(line)
