import logging
import tempfile
from moviepy import VideoFileClip
from uuid import UUID, uuid4
from datetime import datetime, timezone
from src.domain.entities.video import Video, VideoStatus
from src.domain.exceptions import VideoNotFoundError, VideoUploadError
from src.domain.interfaces.video_repository import VideoRepositoryProtocol
from src.infrastructure.storage.s3_client import S3Client

logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self, repo: VideoRepositoryProtocol, storage: S3Client):
        self._repo = repo
        self._storage = storage

    async def upload_video(self, title: str, description: str, file_bytes: bytes, filename: str, user_id: UUID) -> Video:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(file_bytes)
            tmpname = tmp.name

        try:
            try:
                with VideoFileClip(tmpname) as clip:
                    duration = round(clip.duration)
            except Exception as e:
                logger.warning("Failed to extract video duration: %s", e)
                duration = 0

            storage_key = f"{uuid4()}.mp4"

            try:
                await self._storage.upload_file(storage_key, file_bytes)
            except Exception as e:
                raise VideoUploadError(f"S3 upload failed: {e}") from e

            video = Video.create(title, description, storage_key, duration, user_id)
            try:
                await self._repo.add(video)
            except Exception:
                await self._try_cleanup_s3(storage_key)
                raise

            video.status = VideoStatus.READY
            video.updated_at = datetime.now(timezone.utc)
            await self._repo.update_status(video.id, VideoStatus.READY)
        finally:
            import os
            try:
                os.unlink(tmpname)
            except OSError:
                pass

        return video

    async def _try_cleanup_s3(self, key: str):
        try:
            await self._storage.delete_file(key)
        except Exception:
            logger.warning("Failed to clean up S3 object %s", key)

    async def get_video_metadata(self, video_id: UUID) -> Video:
        video = await self._repo.get(video_id)
        if not video:
            raise VideoNotFoundError(video_id)
        return video

    async def get_video_list(self, limit: int = 10, offset: int = 0) -> tuple[list[Video], int]:
        videos = await self._repo.list(limit, offset)
        total = await self._repo.count()
        return videos, total

    async def get_presigned_url(self, storage_key: str) -> str:
        return await self._storage.get_presigned_url(storage_key)

    async def stream_video(self, storage_key: str, range_header: str = None):
        return await self._storage.get_file_stream(storage_key, range_header)

    async def update_video_status(self, video_id: UUID, status: VideoStatus) -> Video:
        video = await self._repo.get(video_id)
        if not video:
            raise VideoNotFoundError(video_id)
        video.status = status
        video.updated_at = datetime.now(timezone.utc)
        await self._repo.update_status(video_id, status)
        return video