from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Application settings loaded from the root .env file."""

    app_name: str = "RoboFusion SCS-RG API"
    app_version: str = "0.1.0"
    app_env: str = "development"

    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str
    database_user: str
    database_password: str

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        """Return the PostgreSQL SQLAlchemy connection URL."""
        return (
            f"postgresql+psycopg://{self.database_user}:"
            f"{self.database_password}@{self.database_host}:"
            f"{self.database_port}/{self.database_name}"
        )


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()


settings = get_settings()