import unittest
from unittest.mock import AsyncMock
from uuid import uuid4

from authorization_service.src.services.auth import AuthService
from authorization_service.src.domain.entities.user import User
from authorization_service.src.domain.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError
)
from authorization_service.src.core.settings import AuthSettings
from pydantic import SecretStr


class TestAuthService(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_repo = AsyncMock()
        self.settings = AuthSettings(
            JWT_SECRET=SecretStr("x" * 32),
            JWT_ALGORITHM="HS256",
            JWT_ACCESS_EXPIRE_MINUTES=30,
            JWT_REFRESH_EXPIRE_DAYS=7
        )
        self.service = AuthService(self.mock_repo, self.settings)

    async def test_register_success(self):
        # Arrange
        email = "test@example.com"
        password = "password123"
        expected_user = User(
            id=uuid4(),
            email=email,
            hashed_password="hashed_password",
            is_active=True
        )

        self.mock_repo.exists_by_email.return_value = False
        self.mock_repo.save.return_value = expected_user

        # Act
        result = await self.service.register(email, password)

        # Assert
        self.assertEqual(result, expected_user)
        self.mock_repo.exists_by_email.assert_called_once_with(email)
        self.mock_repo.save.assert_called_once()

    async def test_register_user_already_exists(self):
        # Arrange
        email = "existing@example.com"
        password = "password123"

        self.mock_repo.exists_by_email.return_value = True

        # Act & Assert
        with self.assertRaises(UserAlreadyExistsError):
            await self.service.register(email, password)

        self.mock_repo.exists_by_email.assert_called_once_with(email)
        self.mock_repo.save.assert_not_called()

    async def test_login_success(self):
        # Arrange
        email = "test@example.com"
        password = "password123"
        user_id = uuid4()
        user = User(
            id=user_id,
            email=email,
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Le0XcJjTx3cdTOBmO",  # bcrypt hash for "password123"
            is_active=True
        )

        self.mock_repo.get_by_email.return_value = user

        # Mock password verification to return True
        with unittest.mock.patch('authorization_service.src.services.auth.verify_password', return_value=True):
            # Act
            result = await self.service.login(email, password)

            # Assert
            self.assertIn("access_token", result)
            self.assertIn("refresh_token", result)
            self.assertEqual(result["token_type"], "Bearer")
            self.mock_repo.get_by_email.assert_called_once_with(email)

    async def test_login_invalid_credentials(self):
        # Arrange
        email = "test@example.com"
        password = "wrong_password"

        self.mock_repo.get_by_email.return_value = None

        # Act & Assert
        with self.assertRaises(InvalidCredentialsError):
            await self.service.login(email, password)

    async def test_login_inactive_user(self):
        # Arrange
        email = "test@example.com"
        password = "password123"
        user = User(
            id=uuid4(),
            email=email,
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Le0XcJjTx3cdTOBmO",  # bcrypt hash for "password123"
            is_active=False
        )

        self.mock_repo.get_by_email.return_value = user

        # Mock password verification to return True
        with unittest.mock.patch('authorization_service.src.services.auth.verify_password', return_value=True):
            # Act & Assert
            with self.assertRaises(InvalidCredentialsError):
                await self.service.login(email, password)

    async def test_get_user_success(self):
        # Arrange
        user_id = uuid4()
        expected_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed",
            is_active=True
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