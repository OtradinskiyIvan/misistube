from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.domain.exceptions import UserNotFoundError, UserDeletionError
from src.services.delete_user import DeleteUserService


class TestDeleteUserService:
    async def test_execute_deletes_user(
        self, mock_repository: AsyncMock, mock_uow: AsyncMock,
    ) -> None:
        user_id = uuid4()
        mock_repository.delete.return_value = True
        service = DeleteUserService(mock_repository, mock_uow)

        result = await service.execute(user_id)

        assert result is True
        mock_repository.delete.assert_awaited_once_with(user_id)
        mock_uow.commit.assert_awaited_once()

    async def test_execute_raises_not_found(
        self, mock_repository: AsyncMock, mock_uow: AsyncMock,
    ) -> None:
        user_id = uuid4()
        mock_repository.delete.side_effect = UserNotFoundError(str(user_id))
        service = DeleteUserService(mock_repository, mock_uow)

        with pytest.raises(UserNotFoundError):
            await service.execute(user_id)

        mock_uow.commit.assert_not_awaited()

    async def test_execute_raises_deletion_error(
        self, mock_repository: AsyncMock, mock_uow: AsyncMock,
    ) -> None:
        user_id = uuid4()
        mock_repository.delete.side_effect = UserDeletionError("DB constraint")
        service = DeleteUserService(mock_repository, mock_uow)

        with pytest.raises(UserDeletionError):
            await service.execute(user_id)

        mock_uow.commit.assert_not_awaited()
