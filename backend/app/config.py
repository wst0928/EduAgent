"""Application configuration with environment variable support."""
from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "EduAgent - 涓€у寲瀛︿範澶氭櫤鑳戒綋绯荤粺"
    app_version: str = "1.0.0"
    debug: bool = True

    # LLM API
    llm_api_key: str = "sk-your-api-key"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "sqlite:///./eduagent.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Agent settings
    max_conversation_history: int = 50
    agent_timeout_seconds: int = 45

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
