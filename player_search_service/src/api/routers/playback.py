from fastapi import APIRouter, HTTPException, Depends
from src.api.schemas import PlaybackUrl
from src.api.deps import get_storage_adapter
from src.infrastructure.storage.protocol import StoragePort
from src.core.config import get_settings
from src.api.deps import get_playback_usecase

router = APIRouter(tags=["playback"])

@router.get("/playback/{video_id}", response_model=PlaybackUrl)
async def get_playback(video_id: str, uc: GetPlaybackUrlUseCase = Depends(get_playback_usecase)):
    return await uc.execute(video_id)