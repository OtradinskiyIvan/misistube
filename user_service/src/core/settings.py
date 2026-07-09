import os
import sys
from pathlib import Path

from pydantic import AliasChoices, Field

ROOT_DIRECTORY = Path(__file__).resolve().parents[3]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

import shared.config as shared_config

SERVICE_DIRECTORY = Path(__file__).resolve().parents[2]
ENV_FILE = SERVICE_DIRECTORY / ".env"


class UserServiceSettings(shared_config.BaseSettings):
    model_config = {
        "env_file": str(ENV_FILE),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "case_sensitive": True,
    }

    APP_NAME: str = "user-service"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = "INFO"
    SERVICE_VERSION: str = "0.1.0"

    DATABASE_URL: shared_config.PostgresDsn
    DATABASE_ECHO: bool = False

    JWT_SECRET: shared_config.SecretStr = Field(validation_alias=AliasChoices("JWT_SECRET", "SECRET_KEY"))
    JWT_ALGORITHM: str = Field(default="HS256", validation_alias=AliasChoices("JWT_ALGORITHM", "JWT_ALGORITHM"))

    INTERNAL_API_KEY: str = ""

    S3_ENDPOINT_URL: str = Field(default="http://localhost:9000", validation_alias=AliasChoices("S3_ENDPOINT_URL", "S3_ENDPOINT"))
    S3_PUBLIC_ENDPOINT_URL: str = Field(default="http://localhost:9002", validation_alias=AliasChoices("S3_PUBLIC_ENDPOINT_URL", "S3_PUBLIC_ENDPOINT"))
    S3_ACCESS_KEY: shared_config.SecretStr = Field(default="minioadmin", validation_alias=AliasChoices("S3_ACCESS_KEY"))
    S3_SECRET_KEY: shared_config.SecretStr = Field(default="minioadmin123", validation_alias=AliasChoices("S3_SECRET_KEY"))
    S3_AVATAR_BUCKET: str = "avatars"


settings = UserServiceSettings()
