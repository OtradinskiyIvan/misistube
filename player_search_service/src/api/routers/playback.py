from uuid import UUID
from fastapi import APIRouter, Depends, Path
from src.api.deps import get_playback_usecase
from src.api.schemas import PlaybackUrl
from src.usecases.playback import GetPlaybackUrlUseCase

router = APIRouter(tags=["playback"])

@router.get("/playback/{video_id}", response_model=PlaybackUrl)
async def get_playback(
    video_id: UUID = Path(..., description="ID видео в формате UUID"),
    usecase: GetPlaybackUrlUseCase = Depends(get_playback_usecase)
):
    return await usecase.execute(str(video_id))
