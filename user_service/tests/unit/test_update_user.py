from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.domain.entities import User
from src.domain.exceptions import UserNotFoundError
from src.services.update_user import UpdateUserService


class TestUpdateUserService:
    async def test_execute_updates_all_fields(
        self, mock_repository: AsyncMock, mock_uow: AsyncMock, sample_user: User,
    ) -> None:
        mock_repository.get_by_id.return_value = sample_user
        updated = User(
            id=sample_user.id,
            username="newname", email="new@example.com", status="inactive",
        )
        mock_repository.update.return_value = updated
        service = UpdateUserService(mock_repository, mock_uow)

        result = await service.execute(
            user_id=sample_user.id,
            username="newname",
            email="new@example.com",
            status="inactive",
        )

        assert result.username == "newname"
        assert result.email == "new@example.com"
        assert result.status == "inactive"
        mock_repository.get_by_id.assert_awaited_once_with(sample_user.id)
        mock_repository.update.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    async def test_execute_partial_update(
        self, mock_repository: AsyncMock, mock_uow: AsyncMock, sample_user: User,
    ) -> None:
        mock_repository.get_by_id.return_value = sample_user
        updated = User(
            id=sample_user.id,
            username=sample_user.username,
            email="changed@example.com",
            status=sample_user.status,
        )
        mock_repository.update.return_value = updated
        service = UpdateUserService(mock_repository, mock_uow)

        result = await service.execute(
            user_id=sample_user.id, email="changed@example.com",
        )

        assert result.email == "changed@example.com"
        assert result.username == sample_user.username
        mock_repository.update.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    async def test_execute_raises_not_found(
        self, mock_repository: AsyncMock, mock_uow: AsyncMock,
    ) -> None:
        user_id = uuid4()
        mock_repository.get_by_id.side_effect = UserNotFoundError(str(user_id))
        service = UpdateUserService(mock_repository, mock_uow)

        with pytest.raises(UserNotFoundError):
            await service.execute(user_id=user_id, username="anything")

        mock_repository.update.assert_not_awaited()
        mock_uow.commit.assert_not_awaited()
