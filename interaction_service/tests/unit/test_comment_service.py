import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from interaction_service.src.services.comment_service import CommentService


@pytest.fixture
def comment_repo():
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
def service(comment_repo, uow, user_service_client):
    return CommentService(comment_repo, uow, user_service_client)


def make_comment(**kwargs):
    c = MagicMock()
    c.id = kwargs.get("id", uuid.uuid4())
    c.user_id = kwargs.get("user_id", uuid.uuid4())
    c.video_id = kwargs.get("video_id", uuid.uuid4())
    c.parent_id = kwargs.get("parent_id", None)
    c.content = kwargs.get("content", "Test comment")
    c.is_edited = False
    c.created_at = kwargs.get("created_at", None)
    c.updated_at = kwargs.get("updated_at", None)
    return c


@pytest.mark.asyncio
async def test_create_comment(service, comment_repo, uow):
    user_id = uuid.uuid4()
    video_id = uuid.uuid4()
    comment = make_comment(user_id=user_id, video_id=video_id, content="Hello")
    comment_repo.create.return_value = comment

    result = await service.create_comment(user_id, video_id, "Hello")

    assert result["content"] == "Hello"
    assert result["user_id"] == user_id
    assert result["video_id"] == video_id
    comment_repo.create.assert_awaited_once_with(user_id, video_id, "Hello", None)
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_video_comments(service, comment_repo):
    video_id = uuid.uuid4()
    c1 = make_comment(video_id=video_id)
    c2 = make_comment(video_id=video_id)
    comment_repo.get_by_video.return_value = [c1, c2]

    result = await service.get_video_comments(video_id)

    assert len(result) == 2


@pytest.mark.asyncio
async def test_update_comment_owned(service, comment_repo, uow):
    user_id = uuid.uuid4()
    comment = make_comment(user_id=user_id, content="Old")
    comment_repo.get_by_id.return_value = comment
    updated = make_comment(user_id=user_id, content="Updated")
    comment_repo.update_content.return_value = updated

    result = await service.update_comment(comment.id, user_id, "Updated")

    assert result is not None
    assert result["content"] == "Updated"
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_comment_not_owned(service, comment_repo, uow):
    owner_id = uuid.uuid4()
    other_id = uuid.uuid4()
    comment = make_comment(user_id=owner_id)
    comment_repo.get_by_id.return_value = comment

    result = await service.update_comment(comment.id, other_id, "Hacked")

    assert result is None
    comment_repo.update_content.assert_not_called()
    uow.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_comment_owned(service, comment_repo, uow):
    user_id = uuid.uuid4()
    comment = make_comment(user_id=user_id)
    comment_repo.get_by_id.return_value = comment
    comment_repo.delete.return_value = True

    result = await service.delete_comment(comment.id, user_id)

    assert result is True
    comment_repo.delete.assert_awaited_once_with(comment.id)
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_comment_not_owned(service, comment_repo, uow):
    owner_id = uuid.uuid4()
    other_id = uuid.uuid4()
    comment = make_comment(user_id=owner_id)
    comment_repo.get_by_id.return_value = comment

    result = await service.delete_comment(comment.id, other_id)

    assert result is False
    comment_repo.delete.assert_not_called()
    uow.commit.assert_not_called()
