from fastapi import APIRouter, Depends

from src.api.deps import get_search_usecase
from src.api.schemas import SearchQuery, SearchResponse
from src.usecases.search import SearchVideoUseCase

router = APIRouter(tags=["search"])

@router.get("/search", response_model=SearchResponse)
async def search_videos(q: SearchQuery = Depends(), uc: SearchVideoUseCase = Depends(get_search_usecase)):
    return await uc.execute(q)
