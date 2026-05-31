# core/config.py
class Settings(BaseSettings):
    # ... существующие настройки ...
    
    # MinIO S3
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin123"
    S3_BUCKET_NAME: str = "videos"
    S3_PRESIGNED_EXPIRY: int = 3600  # 1 час

    class Config:
        env_file = ".env"