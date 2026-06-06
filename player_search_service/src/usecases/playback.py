import logging

from src.api.schemas import PlaybackUrl
from src.core.exceptions import VideoNotFoundError
from src.infrastructure.search.protocol import SearchPort
from src.infrastructure.storage.protocol import StoragePort

logger = logging.getLogger(__name__)


class GetPlaybackUrlUseCase:
    def __init__(
        self,
        storage: StoragePort,
        search_port: SearchPort,
        bucket_name: str,
        expires_in: int
    ):
        self.storage = storage
        self.search_port = search_port
        self.bucket_name = bucket_name
        self.expires_in = expires_in

    async def execute(self, video_id: str) -> PlaybackUrl:
        logger.info("Searching for video_id: %s", video_id)

        video = await self.search_port.get_by_id(video_id)
        if not video:
            logger.error("Video not found: %s", video_id)
            raise VideoNotFoundError(video_id)

        logger.info("Found video: %s, storage_key: %s", video.title, video.storage_key)

        storage_key = video.storage_key

        url, exp = await self.storage.generate_presigned_url(
            object_key=storage_key,
            bucket=self.bucket_name,
            expires_in=self.expires_in
        )
        return PlaybackUrl(hls_master_url=url, expires_at=exp)
