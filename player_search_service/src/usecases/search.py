import logging
from src.api.schemas import SearchQuery, SearchResponse
from src.infrastructure.cache.protocol import CachePort
from src.infrastructure.search.protocol import SearchPort
from src.infrastructure.storage.protocol import StoragePort
from src.infrastructure.user_service.client import UserServiceClient
from src.infrastructure.user_service.cache import UserCacheService

logger = logging.getLogger(__name__)


class SearchVideoUseCase:
    def __init__(
        self, 
        cache: CachePort, 
        search_port: SearchPort,
        storage: StoragePort,
        user_service_client: UserServiceClient,
        user_cache: UserCacheService,
    ):
        self.cache = cache
        self.search_port = search_port
        self.storage = storage
        self.user_service_client = user_service_client
        self.user_cache = user_cache

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

        await self._enrich_usernames(items)

        response = SearchResponse(
            items=items,
            total=total,
            offset=query.offset,
            limit=query.limit
        )
        await self.cache.set(cache_key, response.model_dump(), ttl=300)
        return response

    async def _enrich_usernames(self, items: list) -> None:
        """
        Обогащает список видео реальными username из user service.
        Использует кэш для избежания повторных запросов.
        """
        if not items:
            return
        
        user_ids = list({item.user_id for item in items if item.user_id})
        if not user_ids:
            return
        
        usernames_to_fetch = []
        for user_id in user_ids:
            cached_username = self.user_cache.get(user_id)
            if cached_username:
                for item in items:
                    if item.user_id == user_id:
                        item.username = cached_username
            else:
                usernames_to_fetch.append(user_id)
        
        if not usernames_to_fetch:
            return
        
        logger.info(
            "Fetching usernames for %d users from user service", 
            len(usernames_to_fetch)
        )
        
        fetched_usernames = await self.user_service_client.get_usernames_batch(
            usernames_to_fetch
        )
        
        self.user_cache.set_many(fetched_usernames)
        
        for item in items:
            if item.user_id in fetched_usernames:
                item.username = fetched_usernames[item.user_id]