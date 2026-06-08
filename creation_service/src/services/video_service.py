import io
import logging
import tempfile
from moviepy import VideoFileClip
from PIL import Image
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

    async def upload_video(self, title: str, description: str, file_bytes: bytes, filename: str, user_id: UUID, thumbnail_bytes: bytes | None = None) -> Video:
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

            thumbnail_key = None
            if thumbnail_bytes:
                img = Image.open(io.BytesIO(thumbnail_bytes))
                w, h = img.size
                target_ratio = 16 / 9
                if w / h > target_ratio:
                    new_w = int(h * target_ratio)
                    offset = (w - new_w) // 2
                    img = img.crop((offset, 0, offset + new_w, h))
                else:
                    new_h = int(w / target_ratio)
                    offset = (h - new_h) // 2
                    img = img.crop((0, offset, w, offset + new_h))
                img = img.resize((1280, 720), Image.LANCZOS)
                buf = io.BytesIO()
                img.convert("RGB").save(buf, format="JPEG", quality=85)
                thumbnail_bytes = buf.getvalue()
                thumbnail_key = f"thumbnails/{uuid4()}.jpg"
                try:
                    await self._storage.upload_thumbnail_file(thumbnail_key, thumbnail_bytes)
                except Exception:
                    if storage_key:
                        await self._try_cleanup_s3(storage_key)
                    raise

            video = Video.create(title, storage_key, duration, user_id, description, thumbnail_key=thumbnail_key)
            try:
                await self._repo.add(video)
            except Exception:
                await self._try_cleanup_s3(storage_key)
                if thumbnail_key:
                    await self._try_cleanup_s3_thumbnail(thumbnail_key)
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

    async def _try_cleanup_s3_thumbnail(self, key: str):
        try:
            await self._storage.delete_thumbnail_file(key)
        except Exception:
            logger.warning("Failed to clean up S3 thumbnail %s", key)

    async def get_video_metadata(self, video_id: UUID) -> Video:
        video = await self._repo.get(video_id)
        if not video:
            raise VideoNotFoundError(video_id)
        return video

    async def get_video_list(self, limit: int = 10, offset: int = 0, user_id: UUID | None = None) -> tuple[list[Video], int]:
        videos = await self._repo.list(limit, offset, user_id=user_id)
        total = await self._repo.count(user_id=user_id)
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

    async def delete_video(self, video_id: UUID, user_id: UUID) -> None:
        video = await self.get_video_metadata(video_id)
        if video.user_id != user_id:
            raise PermissionError("You can only delete your own videos")
        if video.status == VideoStatus.DELETED:
            raise VideoNotFoundError(video_id)
        await self._storage.delete_file(video.storage_key)
        if video.thumbnail_key:
            await self._storage.delete_thumbnail_file(video.thumbnail_key)
        await self._repo.update_status(video_id, VideoStatus.DELETED)

    async def stream_thumbnail(self, thumbnail_key: str):
        return await self._storage.get_thumbnail_stream(thumbnail_key)