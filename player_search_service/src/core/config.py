from pydantic import Field, SecretStr, field_validator
from pydantic_settings import SettingsConfigDict
from shared.config import SharedBaseSettings as BaseSettings


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
    SLOW_QUERY_THRESHOLD_MS: int = 100  # миллисекунды

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300

    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_PUBLIC_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: SecretStr = SecretStr("minioadmin")
    S3_SECRET_KEY: SecretStr = SecretStr("minioadmin")
    S3_BUCKET_NAME: str = "videos"
    S3_BUCKET_THUMBNAILS: str = "thumbnails"
    S3_PRESIGNED_URL_EXPIRES: int = 900

    CORS_ALLOW_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])

    USER_SERVICE_URL: str = "http://localhost:8000"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        return v

    @property
    def cors_allow_credentials(self) -> bool:
        """
        В development с allow_origins=["*"] отключаем credentials.
        В production с конкретными origins — включаем.
        """
        return not (self.APP_ENV == "development" and self.CORS_ALLOW_ORIGINS == ["*"])


def get_settings() -> PlayerSearchSettings:
    """Возвращает экземпляр PlayerSearchSettings с валидацией"""
    return PlayerSearchSettings()
