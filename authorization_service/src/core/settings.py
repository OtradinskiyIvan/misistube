import sys
from pathlib import Path

from pydantic import PostgresDsn, SecretStr, field_validator
from pydantic_settings import SettingsConfigDict

from shared.config import SharedBaseSettings

SERVICE_DIRECTORY = Path(__file__).resolve().parents[2]
if str(SERVICE_DIRECTORY.parent) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIRECTORY.parent))

ENV_FILE = SERVICE_DIRECTORY / ".env"


class AuthSettings(SharedBaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Authorization Service"
    DATABASE_URL: PostgresDsn
    JWT_SECRET: SecretStr
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    # SMTP settings for confirmation emails
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 25
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM: str | None = None
    SMTP_USE_TLS: bool = False

    USER_SERVICE_URL: str = "http://user-service:8000"
    INTERNAL_API_KEY: str = ""
    ADMIN_KEY: str | None = None

    S3_ENDPOINT: str | None = None
    S3_ACCESS_KEY: SecretStr | None = None
    S3_SECRET_KEY: SecretStr | None = None
    S3_BUCKET_NAME: str | None = None

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: SecretStr) -> SecretStr:
        if len(v.get_secret_value()) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v
