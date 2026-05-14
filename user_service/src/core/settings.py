import os
import sys
from pathlib import Path
from typing import Optional

ROOT_DIRECTORY = Path(__file__).resolve().parents[3]
if str(ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(ROOT_DIRECTORY))

import shared.config as shared_config


class UserServiceSettings(shared_config.BaseSettings):
    model_config = {
        "env_file": [".env", f".env.{os.getenv('APP_ENV', 'development')}"],
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "case_sensitive": True,
    }

    APP_NAME: str = "user-service"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = "INFO"
    SERVICE_VERSION: str = "0.1.0"

    # Temporary local development defaults: allow running without .env until DB and secrets are set up.
    DATABASE_URL: Optional[shared_config.PostgresDsn] = None
    DATABASE_ECHO: bool = False
    SECRET_KEY: Optional[shared_config.SecretStr] = None

    S3_ENDPOINT: Optional[str] = None
    S3_ACCESS_KEY: Optional[shared_config.SecretStr] = None
    S3_SECRET_KEY: Optional[shared_config.SecretStr] = None
    S3_BUCKET_NAME: Optional[str] = None


settings = UserServiceSettings()
