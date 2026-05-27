from fastapi import APIRouter, HTTPException, Depends
from src.api.schemas import PlaybackUrl
from src.api.deps import get_storage_adapter
from src.infrastructure.storage.protocol import StoragePort
from src.core.config import get_settings

router = APIRouter(tags=["playback"])

@router.get("/playback/{video_id}", response_model=PlaybackUrl)
async def get_playback_url(
    video_id: str,
    storage: StoragePort = Depends(get_storage_adapter)
):
    """Генерация presigned URL для HLS-плеера"""
    object_key = f"{video_id}/master.m3u8"
    
    try:
        url, expires_at = await storage.generate_presigned_url(
            object_key=object_key,
            bucket=get_settings().s3_bucket_videos,
            expires_in=get_settings().s3_presigned_url_expires
        )
        
        return PlaybackUrl(
            hls_master_url=url,
            expires_at=expires_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 error: {str(e)}")