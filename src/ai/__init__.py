"""
AI module — provider factory + public exports.
"""

from src.types import AppConfig
from src.ai.providers import AIProvider, DeepSeekProvider, OpenRouterProvider
from src.ai.prompt_builder import build_prompt

provider = {
    "deepseek": DeepSeekProvider,
    "opennrouter": OpenRouterProvider,
}
def create_ai_provider(config: AppConfig) -> AIProvider:
    
    provider_cls = provider.get(config.provider)

    if not provider_cls:
        raise ValueError(
            f"Unsppported provider: {config.provider}"
        )

    return provider_cls(config)


__all__ = ["create_ai_provider", "build_prompt", "AIProvider"]
