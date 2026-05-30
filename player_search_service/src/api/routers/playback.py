from fastapi import APIRouter, Depends

from src.api.deps import get_playback_usecase
from src.api.schemas import PlaybackUrl
from src.usecases.playback import GetPlaybackUrlUseCase

router = APIRouter(tags=["playback"])

@router.get("/playback/{video_id}", response_model=PlaybackUrl)
async def get_playback(video_id: str, uc: GetPlaybackUrlUseCase = None):
    if uc is None:
        uc = Depends(get_playback_usecase)
    return await uc.execute(video_id)
