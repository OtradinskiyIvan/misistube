from src.api.schemas import PlaybackUrl
from src.infrastructure.storage.protocol import StoragePort


class GetPlaybackUrlUseCase:
    def __init__(
        self, 
        storage: StoragePort, 
        bucket_name: str, 
        expires_in: int
    ):
        self.storage = storage
        self.bucket_name = bucket_name
        self.expires_in = expires_in

    async def execute(self, video_id: str) -> PlaybackUrl:
        url, exp = await self.storage.generate_presigned_url(
            object_key=f"{video_id}/master.m3u8",
            bucket=self.bucket_name,
            expires_in=self.expires_in
        )
        return PlaybackUrl(hls_master_url=url, expires_at=exp)