from pydantic import ValidationError
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from os import getenv

load_dotenv()

class Settings(BaseSettings):
    app_name: str = "player_search_service"
    log_level: str = getenv("LOG_LEVEL")
    database_url: str = getenv("DATABASE_URL")

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    redis_cache_ttl: int = Field(
        default=300,
        description="Default TTL for cache entries (seconds)"
    )
    
    s3_endpoint_url: str = Field(
        default="http://localhost:9000",
        description="MinIO/S3 endpoint URL"
    )
    s3_access_key: str = Field(default="minioadmin")
    s3_secret_key: str = Field(default="minioadmin")
    s3_bucket_videos: str = Field(default="videos")
    s3_bucket_thumbnails: str = Field(default="thumbnails")
    s3_presigned_url_expires: int = Field(
        default=900,
        description="Presigned URL expiration time (seconds)"
    )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        raise SystemExit(f"Configuration error: missing or invalid environment variables.\n{e}") from e