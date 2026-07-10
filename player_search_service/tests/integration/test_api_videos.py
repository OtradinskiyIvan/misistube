import os
import uuid
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("APP_NAME", "player-search-service-test")

from src.api.deps import (
    get_avatar_cache,
    get_storage_adapter,
    get_user_cache,
    get_user_service_client,
)
from src.infrastructure.database.models import Video, VideoStatus
from src.infrastructure.user_service.avatar_cache import AvatarCacheService
from src.infrastructure.user_service.cache import UserCacheService
from src.main import app


@pytest.fixture
def video_test_deps():
    """Override внешние зависимости для эндпоинта videos"""
    mock_storage = AsyncMock()
    mock_storage.generate_thumbnail_url.return_value = "https://minio.test/thumbnails/test.jpg"

    mock_user_client = AsyncMock()
    mock_user_client.get_username.return_value = None
    mock_user_client.get_user_avatar.return_value = None
    mock_user_client.get_usernames_batch.return_value = {}
    mock_user_client.get_avatars_batch.return_value = {}

    user_cache = UserCacheService(ttl_seconds=300)
    avatar_cache = AvatarCacheService(ttl_seconds=300)

    app.dependency_overrides[get_storage_adapter] = lambda: mock_storage
    app.dependency_overrides[get_user_service_client] = lambda: mock_user_client
    app.dependency_overrides[get_user_cache] = lambda: user_cache
    app.dependency_overrides[get_avatar_cache] = lambda: avatar_cache

    yield {
        "mock_storage": mock_storage,
        "mock_user_client": mock_user_client,
        "user_cache": user_cache,
        "avatar_cache": avatar_cache,
    }

    for dep in [get_storage_adapter, get_user_service_client, get_user_cache, get_avatar_cache]:
        app.dependency_overrides.pop(dep, None)


@pytest.mark.asyncio
async def test_video_details_success(db_session, video_test_deps):
    """Успешное получение деталей видео с обогащением username/avatar/thumbnail"""
    user_id = uuid.uuid4()
    video = Video(
        title="Details Test Video",
        storage_key="videos/test/master.m3u8",
        status=VideoStatus.READY,
        duration_seconds=120,
        user_id=user_id,
        thumbnail_key="thumbnails/test.jpg",
    )
    db_session.add(video)
    await db_session.commit()
    await db_session.refresh(video)

    deps = video_test_deps
    deps["mock_user_client"].get_username.return_value = "cooluser"
    deps["mock_user_client"].get_user_avatar.return_value = "https://avatars.test/cooluser.jpg"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/videos/{video.id}/details")

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Details Test Video"
    assert data["username"] == "cooluser"
    assert data["avatar_url"] == "https://avatars.test/cooluser.jpg"
    assert data["thumbnail_url"] == "https://minio.test/thumbnails/test.jpg"
    assert data["status"] == "ready"

    deps["mock_user_client"].get_username.assert_called_once_with(str(user_id))
    deps["mock_user_client"].get_user_avatar.assert_called_once_with(str(user_id))
    deps["mock_storage"].generate_thumbnail_url.assert_called_once_with("thumbnails/test.jpg")


@pytest.mark.asyncio
async def test_video_details_deleted(db_session, video_test_deps):
    """DELETED видео возвращает 404"""
    user_id = uuid.uuid4()
    video = Video(
        title="Deleted Video",
        storage_key="videos/deleted/master.m3u8",
        status=VideoStatus.DELETED,
        duration_seconds=60,
        user_id=user_id,
    )
    db_session.add(video)
    await db_session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/videos/{video.id}/details")

    assert response.status_code == 404
    data = response.json()
    assert "deleted" in data.get("detail", "").lower() or "deleted" in str(data)


@pytest.mark.asyncio
async def test_video_details_not_found(db_session, video_test_deps):
    """Несуществующее видео возвращает 404"""
    fake_id = uuid.uuid4()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/videos/{fake_id}/details")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_video_details_username_from_cache(db_session, video_test_deps):
    """Username берётся из кэша, user service не вызывается"""
    user_id = uuid.uuid4()
    video = Video(
        title="Cached Username Video",
        storage_key="videos/cached/master.m3u8",
        status=VideoStatus.READY,
        duration_seconds=90,
        user_id=user_id,
    )
    db_session.add(video)
    await db_session.commit()
    await db_session.refresh(video)

    deps = video_test_deps
    deps["user_cache"].set(str(user_id), "cached_user")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/videos/{video.id}/details")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "cached_user"
    deps["mock_user_client"].get_username.assert_not_called()


@pytest.mark.asyncio
async def test_video_details_avatar_cached_as_none(db_session, video_test_deps):
    """Avatar в кэше со значением None — не вызывается user service"""
    user_id = uuid.uuid4()
    video = Video(
        title="Cached Avatar None",
        storage_key="videos/avatar-none/master.m3u8",
        status=VideoStatus.READY,
        duration_seconds=90,
        user_id=user_id,
    )
    db_session.add(video)
    await db_session.commit()
    await db_session.refresh(video)

    deps = video_test_deps
    deps["user_cache"].set(str(user_id), "someuser")
    deps["avatar_cache"].set(str(user_id), None)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/videos/{video.id}/details")

    assert response.status_code == 200
    data = response.json()
    assert data["avatar_url"] is None
    deps["mock_user_client"].get_user_avatar.assert_not_called()


@pytest.mark.asyncio
async def test_video_details_user_service_failure(db_session, video_test_deps):
    """User service недоступен — username=user_id, avatar=None"""
    user_id = uuid.uuid4()
    video = Video(
        title="No User Service",
        storage_key="videos/no-user/master.m3u8",
        status=VideoStatus.READY,
        duration_seconds=90,
        user_id=user_id,
    )
    db_session.add(video)
    await db_session.commit()
    await db_session.refresh(video)

    deps = video_test_deps
    deps["mock_user_client"].get_username.return_value = None
    deps["mock_user_client"].get_user_avatar.return_value = None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/videos/{video.id}/details")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == str(user_id)
    assert data["avatar_url"] is None


@pytest.mark.asyncio
async def test_video_details_thumbnail_error(db_session, video_test_deps):
    """Ошибка при генерации thumbnail_url — возвращается None без падения"""
    user_id = uuid.uuid4()
    video = Video(
        title="Thumbnail Error",
        storage_key="videos/thumb-err/master.m3u8",
        status=VideoStatus.READY,
        duration_seconds=90,
        user_id=user_id,
        thumbnail_key="thumbnails/broken.jpg",
    )
    db_session.add(video)
    await db_session.commit()
    await db_session.refresh(video)

    deps = video_test_deps
    deps["mock_storage"].generate_thumbnail_url.side_effect = Exception("S3 unavailable")
    deps["mock_user_client"].get_username.return_value = "thumbuser"
    deps["mock_user_client"].get_user_avatar.return_value = None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/videos/{video.id}/details")

    assert response.status_code == 200
    data = response.json()
    assert data["thumbnail_url"] is None
    assert data["username"] == "thumbuser"
