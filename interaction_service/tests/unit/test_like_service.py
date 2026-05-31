import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from interaction_service.src.services.like_service import LikeService


@pytest.fixture
def like_repo():
    return AsyncMock()


@pytest.fixture
def uow():
    uow = MagicMock()
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    return uow


@pytest.fixture
def user_service_client():
    return AsyncMock()


@pytest.fixture
def service(like_repo, uow, user_service_client):
    return LikeService(like_repo, uow, user_service_client)


@pytest.mark.asyncio
async def test_like_new(service, like_repo, uow):
    user_id = uuid.uuid4()
    video_id = uuid.uuid4()
    like_repo.get_by_user_and_video.return_value = None

    result = await service.like(user_id, video_id)

    assert result is True
    like_repo.add.assert_awaited_once_with(user_id, video_id)
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_like_already_exists(service, like_repo, uow):
    user_id = uuid.uuid4()
    video_id = uuid.uuid4()
    like_repo.get_by_user_and_video.return_value = MagicMock()

    result = await service.like(user_id, video_id)

    assert result is False
    like_repo.add.assert_not_called()
    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_unlike(service, like_repo, uow):
    user_id = uuid.uuid4()
    video_id = uuid.uuid4()
    like_repo.remove.return_value = True

    result = await service.unlike(user_id, video_id)

    assert result is True
    like_repo.remove.assert_awaited_once_with(user_id, video_id)
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_is_liked(service, like_repo):
    user_id = uuid.uuid4()
    video_id = uuid.uuid4()
    like_repo.get_by_user_and_video.return_value = MagicMock()

    result = await service.is_liked(user_id, video_id)

    assert result is True


@pytest.mark.asyncio
async def test_get_video_likes_count(service, like_repo):
    video_id = uuid.uuid4()
    like_repo.count_by_video.return_value = 5

    result = await service.get_video_likes_count(video_id)

    assert result == 5
