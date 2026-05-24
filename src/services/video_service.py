# services/video_service.py
from src.domain.entities.video import Video, VideoStatus
from src.domain.interfaces.video_repository import VideoRepositoryProtocol
from src.infrastructure.storage.s3_client import S3Client

class VideoService:
    def __init__(self, repo: VideoRepositoryProtocol, storage: S3Client):
        self._repo = repo
        self._storage = storage
    
    async def upload_video(self, title: str, description: str, file_bytes: bytes, filename: str) -> Video:
        # 1. Генерация ключа в S3
        storage_key = f"videos/{uuid4()}.mp4"
        
        # 2. Сохраняем файл в S3
        await self._storage.upload(storage_key, file_bytes)
        
        # 3. Создаём доменную сущность (статус UPLOADING)
        video = Video.create(title, description, storage_key)
        
        # 4. Сохраняем метаданные в БД
        await self._repo.add(video)
        
        # 5. (В будущем: отправить событие в очередь для транскодирования)
        return video
    
    async def get_video_metadata(self, video_id: UUID) -> Video:
        video = await self._repo.get(video_id)
        if not video:
            raise VideoNotFoundError(video_id)
        return video
    
    async def update_metadata(self, video_id: UUID, title: str = None, description: str = None) -> Video:
        video = await self.get_video_metadata(video_id)
        if title:
            video.title = title
        if description:
            video.description = description
        video.updated_at = datetime.utcnow()
        await self._repo.update(video)
        return video
    
    async def get_video_list(self, limit: int = 10, offset: int = 0) -> list[Video]:
        return await self._repo.list(limit, offset)