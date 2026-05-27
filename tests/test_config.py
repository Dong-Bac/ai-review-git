"""
Tests for config loader.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.config import load_config
from src.types import AppConfig


# Keys that load_config reads from environment
_CONFIG_KEYS = [
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_MODEL",
    "DEEPSEEK_BASE_URL",
    "AI_MAX_TOKENS",
    "PROVIDER",
    "APP_NAME",
    "APP_URL",
    "VECTOR_MEMORY_ENABLED",
    "MEMORY_TOP_K",
    "VECTOR_DB_PATH",
    "EMBEDDING_MODEL",
]


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch: pytest.MonkeyPatch):
    """Clear all config-related env vars before each test."""
    for key in _CONFIG_KEYS:
        monkeypatch.delenv(key, raising=False)


class TestLoadConfig:
    """Tests for load_config()."""

    def test_raises_on_missing_api_key(self, tmp_path: Path):
        """Should raise ValueError when DEEPSEEK_API_KEY is missing."""
        env_file = tmp_path / ".env"
        env_file.write_text("SOME_OTHER_KEY=abc\n", encoding="utf-8")

        with pytest.raises(ValueError, match="Missing DEEPSEEK_API_KEY"):
            load_config(env_path=tmp_path)

    def test_loads_minimal_config(self, tmp_path: Path):
        """Should load config with just the API key."""
        env_file = tmp_path / ".env"
        env_file.write_text('DEEPSEEK_API_KEY=sk-test-key-123\n', encoding="utf-8")

        config = load_config(env_path=tmp_path)

        assert isinstance(config, AppConfig)
        assert config.api_key == "sk-test-key-123"
        assert config.model == "deepseek-chat"  # default
        assert config.base_url == "https://api.deepseek.com"  # default
        assert config.max_tokens == 8192  # default
        assert config.provider == "deepseek"  # default

    def test_loads_full_config(self, tmp_path: Path):
        """Should load all config values from .env."""
        env_content = """
DEEPSEEK_API_KEY=sk-full-key
DEEPSEEK_MODEL=deepseek-reasoner
DEEPSEEK_BASE_URL=https://custom.api.com
AI_MAX_TOKENS=4096
PROVIDER=openrouter
APP_NAME=my-review
APP_URL=https://github.com/me/my-review
VECTOR_MEMORY_ENABLED=false
MEMORY_TOP_K=5
EMBEDDING_MODEL=all-mpnet-base-v2
"""
        env_file = tmp_path / ".env"
        env_file.write_text(env_content.strip(), encoding="utf-8")

        config = load_config(env_path=tmp_path)

        assert config.api_key == "sk-full-key"
        assert config.model == "deepseek-reasoner"
        assert config.base_url == "https://custom.api.com"
        assert config.max_tokens == 4096
        assert config.provider == "openrouter"
        assert config.app_name == "my-review"
        assert config.app_url == "https://github.com/me/my-review"
        assert config.memory.enabled is False
        assert config.memory.top_k == 5
        assert config.embedding_model == "all-mpnet-base-v2"

    def test_trims_whitespace(self, tmp_path: Path):
        """Should strip whitespace from env values."""
        env_file = tmp_path / ".env"
        env_file.write_text('DEEPSEEK_API_KEY=  sk-key-with-spaces  \n', encoding="utf-8")

        config = load_config(env_path=tmp_path)

        assert config.api_key == "sk-key-with-spaces"

    def test_memory_defaults(self, tmp_path: Path):
        """Should use sensible defaults for memory config."""
        env_file = tmp_path / ".env"
        env_file.write_text('DEEPSEEK_API_KEY=sk-key\n', encoding="utf-8")

        config = load_config(env_path=tmp_path)

        assert config.memory.enabled is True  # default
        assert config.memory.top_k == 3  # default
        assert config.memory.db_path == ".roo/memory/vector_db"  # default
