from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas import SearchQuery, SearchResponse, VideoResult
from src.api.deps import get_cache_adapter
from src.infrastructure.cache.protocol import CachePort
from src.core.logger import get_logger
from src.api.deps import get_search_usecase

router = APIRouter(tags=["search"])
logger = get_logger("player_search_service", level="INFO")

@router.get("/search", response_model=SearchResponse)
async def search_videos(q: SearchQuery = Depends(), uc: SearchVideoUseCase = Depends(get_search_usecase)):
    return await uc.execute(q)