from src.api.schemas import SearchQuery, SearchResponse
from src.infrastructure.cache.protocol import CachePort
from src.infrastructure.search.protocol import SearchPort

class SearchVideoUseCase:
    def __init__(self, cache: CachePort, search_port: SearchPort):
        self.cache = cache
        self.search_port = search_port

    async def execute(self, query: SearchQuery) -> SearchResponse:
        cache_key = f"search:{query.q}:{query.offset}:{query.limit}"
        
        if cached := await self.cache.get(cache_key):
            return SearchResponse(**cached)

        items, total = await self.search_port.search(
            query=query.q,
            tags=query.tags,
            offset=query.offset,
            limit=query.limit
        )

        response = SearchResponse(
            items=items,
            total=total,
            offset=query.offset,
            limit=query.limit
        )
        await self.cache.set(cache_key, response.model_dump(), ttl=300)
        return response