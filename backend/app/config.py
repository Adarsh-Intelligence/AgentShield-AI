from __future__ import annotations

import json
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application Settings
    APP_ENV: str = "development"
    APP_NAME: str = "AgentShield AI"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Cryptography & Security
    SECRET_KEY: str = "replace-with-a-very-long-and-secure-random-secret-key-32-chars-min"
    ENCRYPTION_KEY: str = "dGhpcy1pcy1hLXNhbXBsZS1mZXJuZXQta2V5LTMyeWVhcm9sZD0="
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "sqlite:///./agentshield.db"

    # Message Broker / Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # AI Providers (optional global defaults)
    GROQ_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Network & SSRF
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_AGENT_HOSTS: List[str] = []
    ALLOW_PRIVATE_IPS_FOR_TESTING: bool = False
    REQUEST_TIMEOUT_SECONDS: int = 30
    MAX_REQUEST_BODY_BYTES: int = 10 * 1024 * 1024  # 10 MB

    # Logging & Metrics
    LOG_LEVEL: str = "INFO"
    PROMETHEUS_ENABLED: bool = True

    @field_validator("CORS_ORIGINS", "ALLOWED_AGENT_HOSTS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: object) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() in ("production", "prod")

    @property
    def broker_url(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def result_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL


settings = Settings()

