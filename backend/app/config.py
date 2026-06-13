"""Configuración de la aplicación.

Todas las variables sensibles se leen desde entorno. Nunca hardcodear secretos.
"""
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

    # --- Entorno ---
    app_env: str = "production"  # "development" | "production"
    app_name: str = "Generador de Contenido IA"

    # --- Base de datos ---
    # Railway entrega DATABASE_URL automáticamente al asociar un Postgres plugin.
    database_url: str

    # --- Seguridad JWT ---
    secret_key: str  # generar con: python -c "import secrets; print(secrets.token_urlsafe(64))"
    access_token_expire_minutes: int = 60 * 24  # 24 horas
    jwt_algorithm: str = "HS256"

    # --- Usuario admin inicial (se crea solo si no hay usuarios en la BD) ---
    admin_email: str
    admin_password: str

    # --- IA (Anthropic) ---
    anthropic_api_key: str
    anthropic_model: str = "claude-haiku-4-5-20251001"
    anthropic_max_tokens: int = 1024
    anthropic_timeout_seconds: float = 20.0

    # --- CORS (solo necesario en desarrollo local, frontend en otro puerto) ---
    cors_origins: str = ""  # coma-separados: "http://localhost:5173,http://localhost:3000"

    # --- Servidor ---
    port: int = 8000  # Railway inyecta PORT automáticamente

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        """Railway/Heroku a veces entregan 'postgres://', pero SQLAlchemy v2 espera 'postgresql://'."""
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        # Forzar driver psycopg v3 si no se especifica
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
    return Settings()  # type: ignore[call-arg]
