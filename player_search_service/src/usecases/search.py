from src.api.schemas import SearchQuery, SearchResponse, VideoResult
from src.infrastructure.cache.protocol import CachePort


class SearchVideoUseCase:
    def __init__(self, cache: CachePort):
        self.cache = cache

    async def execute(self, query: SearchQuery) -> SearchResponse:
        key = f"search:{query.q}:{query.offset}:{query.limit}"
        if cached := await self.cache.get(key):
            return SearchResponse(**cached)

        # 🔸 Заглушка (позже → RepositoryPort)
        resp = SearchResponse(items=[VideoResult(id="v1", title=f"Result for {query.q}", duration=120, tags=[])], total=1, offset=query.offset, limit=query.limit)
        await self.cache.set(key, resp.model_dump(), ttl=300)
        return resp
