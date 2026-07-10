from fastapi import APIRouter, Depends, Query

from src.api.deps import get_search_usecase
from src.api.schemas import SearchQuery, SearchResponse
from src.usecases.search import SearchVideoUseCase

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search_videos(
    q: str | None = Query(None, max_length=255),
    tags: list[str] = Query(default=[], alias="tags"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    usecase: SearchVideoUseCase = Depends(get_search_usecase),
):
    query_obj = SearchQuery(q=q, tags=tags if tags else None, offset=offset, limit=limit)
    return await usecase.execute(query_obj)
