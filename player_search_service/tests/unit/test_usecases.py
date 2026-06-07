from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from src.api.schemas import SearchQuery
from src.usecases.playback import GetPlaybackUrlUseCase
from src.usecases.search import SearchVideoUseCase
from src.core.exceptions import VideoNotFoundError


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
            "items": [{
                "id": "c1",
                "title": "Cached",
                "description": None,
                "storage_key": "videos/cached/master.m3u8",
                "status": "ready",
                "duration_seconds": 60,
                "created_at": "2026-06-05T10:00:00+00:00",
                "updated_at": "2026-06-05T10:00:00+00:00",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "cached_user",

                "tags": None,
                "thumbnail_url": None
            }],
            "total": 1, "offset": 0, "limit": 10
        }
        uc = SearchVideoUseCase(cache=mock_cache, search_port=AsyncMock())

        result = await uc.execute(SearchQuery(q="cached", limit=10))

        mock_cache.get.assert_called_once()
        uc.search_port.search.assert_not_called()
        assert result.items[0].title == "Cached"
        assert result.items[0].user_id == "123e4567-e89b-12d3-a456-426614174000"
        assert result.items[0].username == "cached_user"  

    @pytest.mark.asyncio
    async def test_generate_url(self, mock_storage, mock_search_port):
        """Генерация presigned URL для видео"""
        mock_video = AsyncMock()
        mock_video.storage_key = "video-123/master.m3u8"
        mock_search_port.get_by_id.return_value = mock_video

        mock_storage.generate_presigned_url.return_value = (
            "https://fake-s3.url/video.m3u8",
            datetime.now(UTC) + timedelta(minutes=15)
        )

        uc = GetPlaybackUrlUseCase(
            storage=mock_storage,
            search_port=mock_search_port,
            bucket_name="test-videos",
            expires_in=900
        )

        result = await uc.execute("video-123")

        assert result.hls_master_url == "https://fake-s3.url/video.m3u8"

        mock_storage.generate_presigned_url.assert_called_once_with(
            object_key="video-123/master.m3u8",
            bucket="test-videos",
            expires_in=900
        )

    @pytest.mark.asyncio
    async def test_generate_url_video_not_found(self, mock_storage, mock_search_port):
        """GetPlaybackUrlUseCase выбрасывает VideoNotFoundError, если видео не найдено"""
        mock_search_port.get_by_id.return_value = None

        uc = GetPlaybackUrlUseCase(
            storage=mock_storage,
            search_port=mock_search_port,
            bucket_name="test-videos",
            expires_in=900
        )

        with pytest.raises(VideoNotFoundError) as exc_info:
            await uc.execute("non-existent-id")

        assert exc_info.value.video_id == "non-existent-id"
        assert "non-existent-id" in str(exc_info.value)

        mock_storage.generate_presigned_url.assert_not_called()