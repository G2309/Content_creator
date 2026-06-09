from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "production"  # "development" | "production"
    app_name: str = "Generador de Contenido IA"

    database_url: str

    secret_key: str  
    access_token_expire_minutes: int = 60 * 24  
    jwt_algorithm: str = "HS256"

    admin_email: str
    admin_password: str

    anthropic_api_key: str
    anthropic_model: str = "claude-haiku-4-5-20251001"
    anthropic_max_tokens: int = 1024
    anthropic_timeout_seconds: float = 20.0

    cors_origins: str = ""  

    port: int = 8000 

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        if v.startswith("postgresql://") and "+psycopg" not in v:
            v = v.replace("postgresql://", "postgresql+psycopg://", 1)
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.cors_origins:
            return []
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()  
