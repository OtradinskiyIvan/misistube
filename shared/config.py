from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, SecretStr


class BaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    APP_NAME: str
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: PostgresDsn
    DATABASE_ECHO: bool = False

    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: SecretStr
    S3_SECRET_KEY: SecretStr
    S3_BUCKET_NAME: str