from src.api.schemas import PlaybackUrl
from src.infrastructure.storage.protocol import StoragePort
from src.infrastructure.search.protocol import SearchPort
from fastapi import HTTPException

import logging

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
        logger.info(f"Searching for video_id: {video_id}")

        video = await self.search_port.get_by_id(video_id)
        if not video:
            logger.error(f"Video not found: {video_id}")
            raise HTTPException(status_code=404, detail="Video not found")
        
        logger.info(f"Found video: {video.title}, storage_key: {video.storage_key}")

        storage_key = video.storage_key
        
        
        # if not storage_key.startswith("videos/"):
        #     storage_key = f"videos/{storage_key}"
        
        url, exp = await self.storage.generate_presigned_url(
            object_key=storage_key,
            bucket=self.bucket_name,
            expires_in=self.expires_in
        )
        return PlaybackUrl(hls_master_url=url, expires_at=exp)