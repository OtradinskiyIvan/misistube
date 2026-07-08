import unittest
from unittest.mock import AsyncMock
from uuid import uuid4

from pydantic import PostgresDsn, SecretStr

from shared.security import hash_password

from ..src.core.settings import AuthSettings
from ..src.domain.entities.user import User
from ..src.domain.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from ..src.services.auth import AuthService


class TestAuthService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_repo = AsyncMock()

        self.settings = AuthSettings(
            DATABASE_URL=PostgresDsn("postgresql://test:test@localhost/test"),
            S3_ENDPOINT="http://localhost:9000",
            S3_ACCESS_KEY=SecretStr("test"),
            S3_SECRET_KEY=SecretStr("test"),
            S3_BUCKET_NAME="test",
            JWT_SECRET=SecretStr("x" * 32),
            JWT_ALGORITHM="HS256",
            JWT_ACCESS_EXPIRE_MINUTES=30,
            JWT_REFRESH_EXPIRE_DAYS=7,
        )

        self.service = AuthService(self.mock_repo, self.settings)

    async def test_register_success(self):
        # Arrange
        username = "testuser"
        email = "test@example.com"
        password = "password123"
        expected_user = User(
            id=uuid4(), username=username, email=email, hashed_password="hashed_password", is_active=True
        )

        self.mock_repo.exists_by_email.return_value = False
        self.mock_repo.exists_by_username.return_value = False
        self.mock_repo.save.return_value = expected_user

        # Act
        result = await self.service.register(username, email, password)

        # Assert
        self.assertEqual(result, expected_user)
        self.mock_repo.exists_by_email.assert_called_once_with(email)
        self.mock_repo.exists_by_username.assert_called_once_with(username)
        self.mock_repo.save.assert_called_once()

    async def test_register_user_already_exists(self):
        # Arrange
        username = "existinguser"
        email = "existing@example.com"
        password = "password123"

        self.mock_repo.exists_by_email.return_value = True
        self.mock_repo.exists_by_username.return_value = False

        # Act & Assert
        with self.assertRaises(UserAlreadyExistsError):
            await self.service.register(username, email, password)

        self.mock_repo.exists_by_email.assert_called_once_with(email)
        self.mock_repo.save.assert_not_called()

    async def test_login_success(self):
        # Arrange
        username = "testuser"
        email = "test@example.com"
        password = "password123"
        user_id = uuid4()

        # Создаём реальный хеш пароля
        hashed = hash_password(password)

        user = User(id=user_id, username=username, email=email, hashed_password=hashed, is_active=True)

        self.mock_repo.get_by_email.return_value = user

        # Act
        result = await self.service.login(email, password)

        # Assert
        self.assertIn("access_token", result)
        self.assertIn("refresh_token", result)
        self.assertEqual(result["token_type"], "Bearer")
        self.mock_repo.get_by_email.assert_called_once_with(email)

    async def test_login_invalid_credentials(self):
        # Arrange
        login = "test@example.com"
        password = "wrong_password"

        self.mock_repo.get_by_email.return_value = None
        self.mock_repo.get_by_username.return_value = None

        # Act & Assert
        with self.assertRaises(InvalidCredentialsError):
            await self.service.login(login, password)

    async def test_login_inactive_user(self):
        # Arrange
        username = "testuser"
        email = "test@example.com"
        password = "password123"

        # Создаём реальный хеш пароля
        hashed = hash_password(password)

        user = User(id=uuid4(), username=username, email=email, hashed_password=hashed, is_active=False)

        self.mock_repo.get_by_email.return_value = user

        # Act & Assert
        with self.assertRaises(InvalidCredentialsError):
            await self.service.login(email, password)

    async def test_get_user_success(self):
        # Arrange
        user_id = uuid4()
        expected_user = User(
            id=user_id, username="testuser", email="test@example.com", hashed_password="hashed", is_active=True
        )

        self.mock_repo.get_by_id.return_value = expected_user

        # Act
        result = await self.service.get_user(user_id)

        # Assert
        self.assertEqual(result, expected_user)
        self.mock_repo.get_by_id.assert_called_once_with(user_id)

    async def test_get_user_not_found(self):
        # Arrange
        user_id = uuid4()
        self.mock_repo.get_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(UserNotFoundError):
            await self.service.get_user(user_id)


if __name__ == "__main__":
    unittest.main()
