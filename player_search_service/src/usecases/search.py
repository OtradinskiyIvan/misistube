from src.api.schemas import SearchQuery, SearchResponse
from src.infrastructure.cache.protocol import CachePort
from src.infrastructure.search.protocol import SearchPort
from src.infrastructure.storage.protocol import StoragePort


class SearchVideoUseCase:
    def __init__(
        self, 
        cache: CachePort, 
        search_port: SearchPort,
        storage: StoragePort,
    ):
        self.cache = cache
        self.search_port = search_port
        self.storage = storage

    async def execute(self, query: SearchQuery) -> SearchResponse:
        tags_str = ','.join(sorted(query.tags)) if query.tags else 'none'
        cache_key = f"search:{query.q or 'none'}:{tags_str}:{query.offset}:{query.limit}"

        if cached := await self.cache.get(cache_key):
            return SearchResponse(**cached)

        items, total = await self.search_port.search(
            query=query.q,
            tags=query.tags,
            offset=query.offset,
            limit=query.limit
        )

        for item in items:
            if item.thumbnail_key:
                item.thumbnail_url = await self.storage.generate_thumbnail_url(
                    item.thumbnail_key
                )

        response = SearchResponse(
            items=items,
            total=total,
            offset=query.offset,
            limit=query.limit
        )
        await self.cache.set(cache_key, response.model_dump(), ttl=300)
        return response
