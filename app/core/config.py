import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    github_app_id: str | None = None
    github_private_key_path: str | None = None
    github_private_key: str | None = None
    github_webhook_secret: str | None = None
    github_pat: str | None = None
    
    # LLM Settings
    default_llm_provider: str = "gemini" # gemini, openai, anthropic
    gemini_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
