import unittest
from unittest.mock import AsyncMock
from uuid import uuid4

from pydantic import PostgresDsn, SecretStr

from shared.security import create_jwt_token

from ..src.core.settings import AuthSettings
from ..src.domain.entities.user import User
from ..src.domain.exceptions import InvalidCredentialsError
from ..src.services.auth import AuthService


class TestRefreshToken(unittest.IsolatedAsyncioTestCase):
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

    def _create_refresh_token(self, user_id: str, roles: list[str] | None = None) -> str:
        return create_jwt_token(
            subject=user_id,
            secret=self.settings.JWT_SECRET,
            algorithm=self.settings.JWT_ALGORITHM,
            expires_minutes=30,
            username="testuser",
            email="test@example.com",
            token_type="refresh",
            roles=roles or [],
        )

    def _create_access_token(self, user_id: str) -> str:
        return create_jwt_token(
            subject=user_id,
            secret=self.settings.JWT_SECRET,
            algorithm=self.settings.JWT_ALGORITHM,
            expires_minutes=30,
            username="testuser",
            email="test@example.com",
            token_type="access",
        )

    async def test_refresh_token_success(self):
        user_id = uuid4()
        refresh_token = self._create_refresh_token(str(user_id))
        user = User(id=user_id, username="testuser", email="test@example.com", hashed_password="hashed", is_active=True)
        self.mock_repo.get_by_id.return_value = user

        result = await self.service.refresh_access_token(refresh_token)

        self.assertIn("access_token", result)
        self.assertEqual(result["token_type"], "Bearer")
        self.mock_repo.get_by_id.assert_called_once_with(user_id)

    async def test_refresh_token_invalid_token(self):
        with self.assertRaises(InvalidCredentialsError):
            await self.service.refresh_access_token("invalid.jwt.token")

    async def test_refresh_token_wrong_type(self):
        user_id = uuid4()
        access_token = self._create_access_token(str(user_id))

        with self.assertRaises(InvalidCredentialsError):
            await self.service.refresh_access_token(access_token)

    async def test_refresh_token_user_not_found(self):
        user_id = uuid4()
        refresh_token = self._create_refresh_token(str(user_id))
        self.mock_repo.get_by_id.return_value = None

        with self.assertRaises(InvalidCredentialsError):
            await self.service.refresh_access_token(refresh_token)

    async def test_refresh_token_inactive_user(self):
        user_id = uuid4()
        refresh_token = self._create_refresh_token(str(user_id))
        user = User(
            id=user_id, username="testuser", email="test@example.com", hashed_password="hashed", is_active=False
        )
        self.mock_repo.get_by_id.return_value = user

        with self.assertRaises(InvalidCredentialsError):
            await self.service.refresh_access_token(refresh_token)

    async def test_refresh_token_missing_sub(self):
        secret = self.settings.JWT_SECRET
        algorithm = self.settings.JWT_ALGORITHM
        token = create_jwt_token(
            subject="",
            secret=secret,
            algorithm=algorithm,
            expires_minutes=30,
            username="testuser",
            email="test@example.com",
            token_type="refresh",
        )

        with self.assertRaises(InvalidCredentialsError):
            await self.service.refresh_access_token(token)


if __name__ == "__main__":
    unittest.main()
