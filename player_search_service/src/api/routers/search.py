from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas import SearchQuery, SearchResponse, VideoResult
from src.api.deps import get_cache_adapter
from src.infrastructure.cache.protocol import CachePort
from src.core.logger import get_logger

router = APIRouter(tags=["search"])
logger = get_logger("player_search_service", level="INFO")

@router.get("/search", response_model=SearchResponse)
async def search_videos(
    query: SearchQuery = Depends(),
    cache: CachePort = Depends(get_cache_adapter)
):
    """Поиск видео с кешированием"""
    cache_key = f"search:{query.q}:{query.offset}:{query.limit}"
    
    logger.info("search_requested", extra={"query": query.q, "cache_key": cache_key})
    cached_result = await cache.get(cache_key)
    
    if cached_result:
        logger.info("cache_hit", extra={"key": cache_key})
        return SearchResponse(**cached_result)


    logger.info("cache_miss", extra={"key": cache_key})
    results = [
        VideoResult(
            id="v1",
            title=f"Result for {query.q}",
            duration=120,
            tags=["demo"]
        )
    ]
    
    response = SearchResponse(
        items=results,
        total=1,
        offset=query.offset,
        limit=query.limit
    )
    
    await cache.set(cache_key, response.model_dump(), ttl=60)
    logger.info("search_completed", extra={"results_count": len(results)})
    
    return response