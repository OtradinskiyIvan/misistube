import tempfile
from moviepy.editor import VideoFileClip   # если используешь moviepy
from uuid import uuid4
from datetime import datetime
from src.domain.entities.video import Video, VideoStatus
from src.domain.interfaces.video_repository import VideoRepositoryProtocol
from src.infrastructure.storage.s3_client import S3Client

class VideoService:
    def __init__(self, repo: VideoRepositoryProtocol, storage: S3Client):
        self._repo = repo
        self._storage = storage

    async def upload_video(self, title: str, description: str, file_bytes: bytes, filename: str) -> Video:
        # Сохраняем во временный файл, чтобы прочитать продолжительность
        with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp:
            tmp.write(file_bytes)
            tmp.flush()
            # Извлекаем длительность (если moviepy не установлен — можно временно закомменsтировать или передавать 0)
            try:
                with VideoFileClip(tmp.name) as clip:
                    duration = int(clip.duration)
            except Exception:
                duration = 0   # fallback, если не удалось определить

        storage_key = f"{uuid4()}.mp4"
        await self._storage.upload_file(storage_key, file_bytes)
        video = Video.create(title, description, storage_key, duration)
        await self._repo.add(video)
        return video