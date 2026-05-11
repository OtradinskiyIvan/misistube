from fastapi import APIRouter
from src.api.schemas import PlaybackUrl
from datetime import datetime, timedelta

router = APIRouter(tags=["playback"])

@router.get("/playback/{video_id}", response_model=PlaybackUrl)
async def get_playback_url(video_id: str):
    """Presigned URL для HLS (заглушка)"""
    return PlaybackUrl(
        hls_master_url=f"https://s3.example.com/{video_id}/master.m3u8",
        expires_at=datetime.utcnow() + timedelta(minutes=15)
    )