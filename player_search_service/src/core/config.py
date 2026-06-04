from pydantic import SecretStr, field_validator
from pydantic_settings import SettingsConfigDict

from shared.config import BaseSettings


class PlayerSearchSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Player & Searching Service"
    APP_ENV: str = "development"  # development | staging | production
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300

    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: SecretStr = SecretStr("minioadmin")
    S3_BUCKET_NAME: str = "videos"
    S3_BUCKET_THUMBNAILS: str = "thumbnails"
    S3_PRESIGNED_URL_EXPIRES: int = 900

    CORS_ALLOW_ORIGINS: list[str] = ["*"]

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        return v


def get_settings() -> Settings:
    """Возвращает экземпляр PlayerSearchSettings с валидацией"""
    return PlayerSearchSettings()