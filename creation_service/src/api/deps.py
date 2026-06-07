from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.infrastructure.database.session import get_async_session
from src.infrastructure.repositories.video_repository import SQLAlchemyVideoRepository
from src.infrastructure.storage.s3_client import S3Client
from src.services.video_service import VideoService
from src.core.config import settings
from shared.security import get_token_payload

async def get_video_service(
    session: AsyncSession = Depends(get_async_session)
) -> VideoService:
    repo = SQLAlchemyVideoRepository(session)
    s3_client = S3Client(
        endpoint_url=settings.S3_ENDPOINT_URL,
        public_endpoint_url=settings.S3_PUBLIC_ENDPOINT_URL,
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        bucket_name=settings.S3_BUCKET_NAME,
    )
    return VideoService(repo, s3_client)

async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
) -> UUID:
    try:
        payload = await get_token_payload(authorization, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Token missing sub claim")
    try:
        return UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user_id in token")