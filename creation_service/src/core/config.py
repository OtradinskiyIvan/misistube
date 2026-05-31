from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Video Studio"
    APP_ENV: str = "development"
    
    # PostgreSQL (async)
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/video_db"
    
    # S3 / MinIO
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin123"
    S3_BUCKET_NAME: str = "videos"
    S3_PRESIGNED_EXPIRY: int = 3600  # 1 час
    
    VITE_API_BASE_URL: str = "http://localhost:5173"
    
    class Config:
        env_file = ".env"

settings = Settings()