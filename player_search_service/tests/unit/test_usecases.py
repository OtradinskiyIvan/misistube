from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.api.schemas import SearchQuery, VideoResult
from src.core.exceptions import VideoNotFoundError
from src.infrastructure.database.models import VideoStatus
from src.usecases.playback import GetPlaybackUrlUseCase
from src.usecases.search import SearchVideoUseCase


class TestSearchVideoUseCase:
    @pytest.mark.asyncio
    async def test_search_cache_miss(self, mock_cache, mock_search_port):
        """Cache miss → запрос к БД → сохранение в кеш"""
        mock_user_cache = MagicMock()
        mock_user_cache.get.return_value = None

        uc = SearchVideoUseCase(
            cache=mock_cache,
            search_port=mock_search_port,
            storage=AsyncMock(),
            user_service_client=AsyncMock(),
            user_cache=mock_user_cache,
        )
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
            "items": [
                {
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
                    "thumbnail_url": None,
                }
            ],
            "total": 1,
            "offset": 0,
            "limit": 10,
        }
        mock_user_cache = MagicMock()
        mock_user_cache.get.return_value = None

        uc = SearchVideoUseCase(
            cache=mock_cache,
            search_port=AsyncMock(),
            storage=AsyncMock(),
            user_service_client=AsyncMock(),
            user_cache=mock_user_cache,
        )

        result = await uc.execute(SearchQuery(q="cached", limit=10))

        mock_cache.get.assert_called_once()
        uc.search_port.search.assert_not_called()  # type: ignore[attr-defined]
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
            datetime.now(UTC) + timedelta(minutes=15),
        )

        uc = GetPlaybackUrlUseCase(
            storage=mock_storage,
            search_port=mock_search_port,
            bucket_name="test-videos",
            expires_in=900,
        )

        result = await uc.execute("video-123")

        assert result.hls_master_url == "https://fake-s3.url/video.m3u8"

        mock_storage.generate_presigned_url.assert_called_once_with(
            object_key="video-123/master.m3u8", bucket="test-videos", expires_in=900
        )

    @pytest.mark.asyncio
    async def test_generate_url_video_not_found(self, mock_storage, mock_search_port):
        """GetPlaybackUrlUseCase выбрасывает VideoNotFoundError, если видео не найдено"""
        mock_search_port.get_by_id.return_value = None

        uc = GetPlaybackUrlUseCase(
            storage=mock_storage,
            search_port=mock_search_port,
            bucket_name="test-videos",
            expires_in=900,
        )

        with pytest.raises(VideoNotFoundError) as exc_info:
            await uc.execute("non-existent-id")

        assert exc_info.value.video_id == "non-existent-id"
        assert "non-existent-id" in str(exc_info.value)

        mock_storage.generate_presigned_url.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_url_deleted_video(self, mock_storage, mock_search_port):
        """DELETED видео выбрасывает VideoNotFoundError"""
        mock_video = AsyncMock()
        mock_video.storage_key = "deleted-video/master.m3u8"
        mock_video.status = VideoStatus.DELETED
        mock_search_port.get_by_id.return_value = mock_video

        uc = GetPlaybackUrlUseCase(
            storage=mock_storage,
            search_port=mock_search_port,
            bucket_name="test-videos",
            expires_in=900,
        )

        with pytest.raises(VideoNotFoundError) as exc_info:
            await uc.execute("deleted-id")

        assert exc_info.value.video_id == "deleted-id"
        mock_storage.generate_presigned_url.assert_not_called()


class TestSearchVideoUseCaseEdgeCases:
    @pytest.mark.asyncio
    async def test_search_thumbnail_generated(self, mock_cache, mock_search_port):
        """Генерация thumbnail_url для видео с thumbnail_key"""
        mock_cache.get.return_value = None
        mock_user_cache = MagicMock()
        mock_user_cache.get.return_value = None
        mock_storage = AsyncMock()
        mock_storage.generate_thumbnail_url.return_value = "https://minio.test/thumb.jpg"

        via_result = VideoResult(
            id="v1",
            title="Thumb Video",
            storage_key="videos/v1/master.m3u8",
            status="ready",
            duration_seconds=60,
            thumbnail_key="thumbnails/v1.jpg",
            user_id="u1",
            username="u1",
        )

        mock_search_port.search.return_value = ([via_result], 1)
        mock_user_client = AsyncMock()
        mock_user_client.get_usernames_batch.return_value = {"u1": "thumbuser"}

        uc = SearchVideoUseCase(
            cache=mock_cache,
            search_port=mock_search_port,
            storage=mock_storage,
            user_service_client=mock_user_client,
            user_cache=mock_user_cache,
        )

        result = await uc.execute(SearchQuery(q="thumb", offset=0, limit=10))

        assert result.items[0].thumbnail_url == "https://minio.test/thumb.jpg"
        mock_storage.generate_thumbnail_url.assert_called_once_with("thumbnails/v1.jpg")

    @pytest.mark.asyncio
    async def test_search_no_thumbnail_key(self, mock_cache, mock_search_port):
        """Без thumbnail_key — thumbnail_url остаётся None"""
        mock_cache.get.return_value = None
        mock_user_cache = MagicMock()
        mock_user_cache.get.return_value = None
        mock_storage = AsyncMock()

        via_result = VideoResult(
            id="v2",
            title="No Thumb",
            storage_key="videos/v2/master.m3u8",
            status="ready",
            duration_seconds=60,
            thumbnail_key=None,
            user_id="u2",
            username="u2",
        )

        mock_search_port.search.return_value = ([via_result], 1)
        mock_user_client = AsyncMock()
        mock_user_client.get_usernames_batch.return_value = {"u2": "notthumb"}

        uc = SearchVideoUseCase(
            cache=mock_cache,
            search_port=mock_search_port,
            storage=mock_storage,
            user_service_client=mock_user_client,
            user_cache=mock_user_cache,
        )

        result = await uc.execute(SearchQuery(q="no-thumb", offset=0, limit=10))

        assert result.items[0].thumbnail_url is None
        mock_storage.generate_thumbnail_url.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_enrich_usernames_mixed_cache(self, mock_cache):
        """Часть username из кэша, часть из user service"""
        mock_cache.get.return_value = None
        mock_search_port = AsyncMock()

        video_cached = VideoResult(
            id="cached-id",
            title="Cached User",
            storage_key="v1/master.m3u8",
            status="ready",
            duration_seconds=30,
            user_id="cached-user-id",
            username="cached-user-id",
        )
        video_fetched = VideoResult(
            id="fetched-id",
            title="Fetched User",
            storage_key="v2/master.m3u8",
            status="ready",
            duration_seconds=45,
            user_id="fetched-user-id",
            username="fetched-user-id",
        )

        mock_search_port.search.return_value = ([video_cached, video_fetched], 2)

        mock_user_cache = MagicMock()
        mock_user_cache.get.side_effect = lambda uid: (
            "cached_name" if uid == "cached-user-id" else None
        )

        mock_user_client = AsyncMock()
        mock_user_client.get_usernames_batch.return_value = {"fetched-user-id": "fetched_name"}

        uc = SearchVideoUseCase(
            cache=mock_cache,
            search_port=mock_search_port,
            storage=AsyncMock(),
            user_service_client=mock_user_client,
            user_cache=mock_user_cache,
        )

        result = await uc.execute(SearchQuery(q="test", offset=0, limit=10))

        assert result.items[0].username == "cached_name"
        assert result.items[1].username == "fetched_name"
        mock_user_client.get_usernames_batch.assert_called_once_with(["fetched-user-id"])
        mock_user_cache.set_many.assert_called_once_with({"fetched-user-id": "fetched_name"})
