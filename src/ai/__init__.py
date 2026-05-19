"""
AI module — provider factory + public exports.
"""

from src.types import AppConfig
from src.ai.providers import AIProvider, DeepSeekProvider
from src.ai.prompt_builder import build_prompt


def create_ai_provider(config: AppConfig) -> AIProvider:
    """
    Factory — returns the appropriate provider based on config.
    Extend this when new providers are added.

    Future:
        "anthropic"  -> AnthropicProvider(config)
        "openai"     -> OpenAIProvider(config)
        "ollama"     -> OllamaProvider(config)
    """
    return DeepSeekProvider(config)


__all__ = ["create_ai_provider", "build_prompt", "AIProvider"]
