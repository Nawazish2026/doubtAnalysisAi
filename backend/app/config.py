from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# backend/app/config.py -> repository root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str = ""
    supabase_url: str = ""
    supabase_jwt_secret: str | None = None
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    app_env: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def taxonomy_path(self) -> Path:
        return PROJECT_ROOT / "data" / "taxonomy.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
