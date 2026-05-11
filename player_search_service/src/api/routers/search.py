from fastapi import APIRouter, Depends
from src.api.schemas import SearchQuery, SearchResponse, VideoResult

router = APIRouter(tags=["search"])

@router.get("/search", response_model=SearchResponse)
async def search_videos(query: SearchQuery = Depends()):
    """Поиск видео (заглушка)"""
    return SearchResponse(
        items=[VideoResult(id="v1", title=f"Test: {query.q}", duration=120)],
        total=1,
        offset=query.offset,
        limit=query.limit
    )