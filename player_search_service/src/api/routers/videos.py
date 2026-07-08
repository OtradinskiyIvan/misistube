import logging
from typing import cast

from fastapi import APIRouter, Depends, HTTPException
from shared.database.session import get_async_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import (
    get_avatar_cache,
    get_storage_adapter,
    get_user_cache,
    get_user_service_client,
)
from src.infrastructure.database.models import Video, VideoStatus
from src.infrastructure.storage.protocol import StoragePort
from src.infrastructure.user_service.avatar_cache import AvatarCacheService
from src.infrastructure.user_service.cache import UserCacheService
from src.infrastructure.user_service.client import UserServiceClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/videos", tags=["videos"])


@router.get("/{video_id}/details")
async def get_video(
    video_id: str,
    session: AsyncSession = Depends(get_async_session),
    storage: StoragePort = Depends(get_storage_adapter),
    user_service_client: UserServiceClient = Depends(get_user_service_client),
    user_cache: UserCacheService = Depends(get_user_cache),
    avatar_cache: AvatarCacheService = Depends(get_avatar_cache),
):
    """
    Получает видео по ID с обогащёнными данными (username, thumbnail_url).
    Использует кэш для username.
    """
    stmt = select(Video).where(Video.id == video_id)
    result = await session.execute(stmt)
    video = result.scalar_one_or_none()

    if not video:
        logger.warning("Video not found: %s", video_id)
        raise HTTPException(status_code=404, detail="Video not found")

    if video.status == VideoStatus.DELETED:
        logger.warning("Attempted to access deleted video: %s", video_id)
        raise HTTPException(status_code=404, detail="Video deleted")

    video_data = {
        "id": str(video.id),
        "title": video.title,
        "description": video.description,
        "storage_key": video.storage_key,
        "status": video.status.value,
        "duration_seconds": video.duration_seconds,
        "thumbnail_key": video.thumbnail_key,
        "thumbnail_url": None,
        "user_id": str(video.user_id),
        "username": str(video.user_id),
        "avatar_url": None,
        "created_at": video.created_at.isoformat(),
        "updated_at": video.updated_at.isoformat(),
    }

    if video.thumbnail_key:
        try:
            video_data["thumbnail_url"] = await storage.generate_thumbnail_url(
                cast(str, video.thumbnail_key)
            )
        except Exception as e:
            logger.warning("Failed to generate thumbnail URL for %s: %s", video_id, e)

    user_id_str = str(video.user_id)

    cached_username = user_cache.get(user_id_str)
    if cached_username:
        video_data["username"] = cached_username
        logger.debug("Username from cache for %s: %s", user_id_str, cached_username)
    else:
        username = await user_service_client.get_username(user_id_str)
        if username:
            video_data["username"] = username
            user_cache.set(user_id_str, username)
            logger.info("Username fetched and cached for %s: %s", user_id_str, username)
        else:
            logger.warning("Failed to fetch username for %s", user_id_str)

    if avatar_cache.has(user_id_str):
        video_data["avatar_url"] = avatar_cache.get(user_id_str)
        logger.debug("Avatar from cache for %s: %s", user_id_str, video_data["avatar_url"])
    else:
        # Запрашиваем из user service
        avatar_url = await user_service_client.get_user_avatar(user_id_str)
        avatar_cache.set(user_id_str, avatar_url)
        video_data["avatar_url"] = avatar_url
        logger.info("Avatar fetched and cached for %s: %s", user_id_str, avatar_url)

    return video_data
