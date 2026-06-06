from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.domain.entities import User
from src.domain.exceptions import UserNotFoundError
from src.services.get_user import GetUserService


class TestGetUserService:
    async def test_by_id_returns_user(
        self, mock_repository: AsyncMock, sample_user: User,
    ) -> None:
        mock_repository.get_by_id.return_value = sample_user
        service = GetUserService(mock_repository)

        result = await service.by_id(sample_user.id)

        assert result == sample_user
        mock_repository.get_by_id.assert_awaited_once_with(sample_user.id)

    async def test_by_id_raises_not_found(
        self, mock_repository: AsyncMock,
    ) -> None:
        user_id = uuid4()
        mock_repository.get_by_id.side_effect = UserNotFoundError(str(user_id))
        service = GetUserService(mock_repository)

        with pytest.raises(UserNotFoundError):
            await service.by_id(user_id)

    async def test_by_username_found(
        self, mock_repository: AsyncMock, sample_user: User,
    ) -> None:
        mock_repository.get_by_username.return_value = sample_user
        service = GetUserService(mock_repository)

        result = await service.by_username("testuser")

        assert result == sample_user
        mock_repository.get_by_username.assert_awaited_once_with("testuser")

    async def test_by_username_not_found(
        self, mock_repository: AsyncMock,
    ) -> None:
        mock_repository.get_by_username.return_value = None
        service = GetUserService(mock_repository)

        result = await service.by_username("nonexistent")

        assert result is None

    async def test_by_email_found(
        self, mock_repository: AsyncMock, sample_user: User,
    ) -> None:
        mock_repository.get_by_email.return_value = sample_user
        service = GetUserService(mock_repository)

        result = await service.by_email("test@example.com")

        assert result == sample_user
        mock_repository.get_by_email.assert_awaited_once_with("test@example.com")

    async def test_by_email_not_found(
        self, mock_repository: AsyncMock,
    ) -> None:
        mock_repository.get_by_email.return_value = None
        service = GetUserService(mock_repository)

        result = await service.by_email("nope@example.com")

        assert result is None

    async def test_all_default_params(
        self, mock_repository: AsyncMock, sample_user: User,
    ) -> None:
        mock_repository.get_all.return_value = [sample_user]
        service = GetUserService(mock_repository)

        result = await service.all()

        assert result == [sample_user]
        mock_repository.get_all.assert_awaited_once_with(skip=0, limit=100)

    async def test_all_custom_params(
        self, mock_repository: AsyncMock, sample_user: User,
    ) -> None:
        mock_repository.get_all.return_value = [sample_user]
        service = GetUserService(mock_repository)

        result = await service.all(skip=10, limit=50)

        assert result == [sample_user]
        mock_repository.get_all.assert_awaited_once_with(skip=10, limit=50)

    async def test_all_clamps_limit(
        self, mock_repository: AsyncMock, sample_user: User,
    ) -> None:
        mock_repository.get_all.return_value = [sample_user]
        service = GetUserService(mock_repository)

        await service.all(skip=0, limit=5000)

        mock_repository.get_all.assert_awaited_once_with(skip=0, limit=1000)

    async def test_all_clamps_negative_skip(
        self, mock_repository: AsyncMock, sample_user: User,
    ) -> None:
        mock_repository.get_all.return_value = [sample_user]
        service = GetUserService(mock_repository)

        await service.all(skip=-5, limit=100)

        mock_repository.get_all.assert_awaited_once_with(skip=0, limit=100)
