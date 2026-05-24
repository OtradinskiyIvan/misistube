# api/deps.py
from fastapi import Depends
from src.infrastructure.database.session import get_async_session
from src.infrastructure.repositories.video_repository import SQLAlchemyVideoRepository
from src.infrastructure.storage.s3_client import S3Client
from src.services.video_service import VideoService
from src.core.config import settings

async def get_video_service(session=Depends(get_async_session)) -> VideoService:
    repo = SQLAlchemyVideoRepository(session)
    s3 = S3Client(settings.S3_ENDPOINT_URL, settings.S3_ACCESS_KEY, settings.S3_SECRET_KEY, settings.S3_BUCKET_NAME)
    return VideoService(repo, s3)