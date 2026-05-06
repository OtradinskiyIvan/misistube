from pydantic import ValidationError
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from os import getenv

load_dotenv()

class Settings(BaseSettings):
    app_name: str = "player_search_service"
    log_level: str = getenv("LOG_LEVEL")
    database_url: str = getenv("DATABASE_URL")


def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        raise SystemExit(f"Configuration error: missing or invalid environment variables.\n{e}") from e