from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.session import get_async_session
from src.infrastructure.repositories.video_repository import SQLAlchemyVideoRepository
from src.infrastructure.storage.s3_client import S3Client          # реальный клиент
from src.services.video_service import VideoService
from src.core.config import settings

async def get_video_service(
    session: AsyncSession = Depends(get_async_session)
) -> VideoService:
    # Репозиторий (БД)
    repo = SQLAlchemyVideoRepository(session)
    
    # S3-клиент (MinIO / AWS)
    s3_client = S3Client(
        endpoint_url=settings.S3_ENDPOINT_URL,
        public_endpoint_url=settings.S3_PUBLIC_ENDPOINT_URL,
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        bucket_name=settings.S3_BUCKET_NAME,
    )
    
    # Сервис (Use case)
    return VideoService(repo, s3_client)