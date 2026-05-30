# tests/unit/test_usecases.py
import pytest

from src.api.schemas import SearchQuery
from src.usecases.playback import GetPlaybackUrlUseCase
from src.usecases.search import SearchVideoUseCase


class TestSearchVideoUseCase:

    @pytest.mark.asyncio
    async def test_search_cache_miss(self, mock_cache, mock_search_port):
        """Cache miss → запрос к БД → сохранение в кеш"""
        uc = SearchVideoUseCase(cache=mock_cache, search_port=mock_search_port)
        query = SearchQuery(q="test", offset=0, limit=10)

        result = await uc.execute(query)

        mock_cache.get.assert_called_once()
        mock_search_port.search.assert_called_once()
        mock_cache.set.assert_called_once()
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_search_cache_hit(self, mock_cache):
        """Cache hit → возврат без запроса к БД"""
        mock_cache.get.return_value = {
            "items": [{"id": "c1", "title": "Cached", "duration": 60, "tags": []}],
            "total": 1, "offset": 0, "limit": 10
        }
        uc = SearchVideoUseCase(cache=mock_cache, search_port=AsyncMock())

        result = await uc.execute(SearchQuery(q="cached", limit=10))

        mock_cache.get.assert_called_once()
        uc.search_port.search.assert_not_called()
        assert result.items[0].title == "Cached"


class TestGetPlaybackUrlUseCase:

    @pytest.mark.asyncio
    async def test_generate_url(self, mock_storage):
        uc = GetPlaybackUrlUseCase(storage=mock_storage)
        result = await uc.execute("video-123")

        mock_storage.generate_presigned_url.assert_called_once()
        assert "fake.url" in result.hls_master_url
