import os
import sys
from pathlib import Path
from typing import Optional

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

    S3_ENDPOINT: Optional[str] = None
    S3_ACCESS_KEY: Optional[shared_config.SecretStr] = None
    S3_SECRET_KEY: Optional[shared_config.SecretStr] = None
    S3_BUCKET_NAME: Optional[str] = None


settings = UserServiceSettings()
