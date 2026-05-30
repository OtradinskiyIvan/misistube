from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.domain.entities import User
from src.domain.exceptions import UserAlreadyExistsError
from src.services.create_user import CreateUserService


class TestCreateUserService:
    async def test_execute_creates_user(
        self, mock_repository: AsyncMock, mock_uow: AsyncMock,
    ) -> None:
        mock_repository.create.return_value = User(
            id=uuid4(), username="newuser", email="new@example.com",
            hashed_password="hashed", status="active",
        )
        service = CreateUserService(mock_repository, mock_uow)

        result = await service.execute(
            username="newuser", email="new@example.com", password="StrongPass1",
        )

        assert result.username == "newuser"
        assert result.email == "new@example.com"
        assert result.status == "active"
        mock_repository.create.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    async def test_execute_raises_on_duplicate(
        self, mock_repository: AsyncMock, mock_uow: AsyncMock,
    ) -> None:
        mock_repository.create.side_effect = UserAlreadyExistsError("username", "taken")
        service = CreateUserService(mock_repository, mock_uow)

        with pytest.raises(UserAlreadyExistsError):
            await service.execute(
                username="taken", email="dup@example.com", password="StrongPass1",
            )

        mock_repository.create.assert_awaited_once()
        mock_uow.commit.assert_not_awaited()

    async def test_execute_hashes_password(
        self, mock_repository: AsyncMock, mock_uow: AsyncMock,
    ) -> None:
        service = CreateUserService(mock_repository, mock_uow)

        await service.execute(
            username="pwdtest", email="pwd@example.com", password="StrongPass1",
        )

        call_args = mock_repository.create.await_args[0][0]
        assert isinstance(call_args, User)
        assert call_args.hashed_password != "StrongPass1"
        assert call_args.hashed_password.startswith("$2b$")
