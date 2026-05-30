from fastapi import APIRouter, Depends

from src.api.deps import get_search_usecase
from src.api.schemas import SearchQuery, SearchResponse
from src.core.logger import get_logger

router = APIRouter(tags=["search"])
logger = get_logger("player_search_service", level="INFO")

@router.get("/search", response_model=SearchResponse)
async def search_videos(q: SearchQuery = Depends(), uc: SearchVideoUseCase = Depends(get_search_usecase)):
    return await uc.execute(q)
