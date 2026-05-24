import os
from pathlib import Path
from dotenv import load_dotenv
from src.types import AppConfig, MemoryConfig
import logging
logger = logging.getLogger(__name__)

def load_config(env_path: Path | None = None) -> AppConfig:
    
    dotenv_file = (env_path / ".env") if env_path else (Path.cwd() / ".env")
    load_dotenv(dotenv_file)
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
        max_tokens=int(os.getenv("AI_MAX_TOKENS", "8192")),
        provider=os.getenv("PROVIDER", "deepseek").strip().lower(),
        memory=MemoryConfig(
            enabled=os.getenv("VECTOR_MEMORY_ENABLED", "true").strip().lower() == "true",
            top_k=int(os.getenv("MEMORY_TOP_K", "3")),
            db_path=os.getenv("VECTOR_DB_PATH", ".roo/memory/vector_db").strip(),
        ),
        embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2").strip(),
    )
