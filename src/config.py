import os
from pathlib import Path
from dotenv import load_dotenv
from src.types import AppConfig

def load_config() -> AppConfig:
    load_dotenv(Path.cwd() / ".env")
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "Missing DEEPSEEK_API_KEY. Please add it to .env file"
        )
    
    return AppConfig(
        api_key = api_key,
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip(),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip(),
        app_name=os.getenv("APP_NAME", "ai-review").strip(),
        app_url=os.getenv("APP_URL", "https://github.com/ai-review/ai-review").strip(),
        max_tokens=int(os.getenv("AI_MAX_TOKENS", "4096")),

    )
