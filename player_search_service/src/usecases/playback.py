from src.api.schemas import PlaybackUrl
from src.core.config import get_settings
from src.infrastructure.storage.protocol import StoragePort


class GetPlaybackUrlUseCase:
    def __init__(self, storage: StoragePort):
        self.storage = storage

    async def execute(self, video_id: str) -> PlaybackUrl:
        settings = get_settings()
        url, exp = await self.storage.generate_presigned_url(f"{video_id}/master.m3u8", settings.S3_BUCKET_NAME, settings.S3_PRESIGNED_URL_EXPIRES)
        return PlaybackUrl(hls_master_url=url, expires_at=exp)
