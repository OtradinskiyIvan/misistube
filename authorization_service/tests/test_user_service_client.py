import unittest
from unittest.mock import AsyncMock, patch

from ..src.infrastructure.clients.user_service_client import UserServiceClient


class TestUserServiceClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = UserServiceClient(base_url="http://user-service:8000", internal_api_key="test-key", timeout=5)
        self.client_no_key = UserServiceClient(base_url="http://user-service:8000", timeout=5)

        self.mock_httpx_patcher = patch("httpx.AsyncClient")
        self.mock_httpx_cls = self.mock_httpx_patcher.start()
        self.mock_client = AsyncMock()
        self.mock_httpx_cls.return_value.__aenter__.return_value = self.mock_client
        self.mock_httpx_cls.return_value.__aexit__.return_value = None

    def tearDown(self):
        self.mock_httpx_patcher.stop()

    async def test_sync_user_success(self):
        mock_response = AsyncMock()
        mock_response.status_code = 200
        self.mock_client.post.return_value = mock_response

        result = await self.client.sync_user("test.jwt.token")

        self.assertTrue(result)
        self.mock_client.post.assert_called_once_with(
            "http://user-service:8000/api/v1/auth/sync",
            json={"token": "test.jwt.token"},
            headers={"Content-Type": "application/json", "X-API-Key": "test-key"},
        )

    async def test_sync_user_failure(self):
        mock_response = AsyncMock()
        mock_response.status_code = 400
        self.mock_client.post.return_value = mock_response

        result = await self.client.sync_user("test.jwt.token")

        self.assertFalse(result)

    async def test_sync_user_no_api_key(self):
        mock_response = AsyncMock()
        mock_response.status_code = 200
        self.mock_client.post.return_value = mock_response

        result = await self.client_no_key.sync_user("test.jwt.token")

        self.assertTrue(result)
        self.mock_client.post.assert_called_once_with(
            "http://user-service:8000/api/v1/auth/sync",
            json={"token": "test.jwt.token"},
            headers={"Content-Type": "application/json"},
        )

    async def test_delete_user_success(self):
        mock_response = AsyncMock()
        mock_response.status_code = 204
        self.mock_client.delete.return_value = mock_response

        result = await self.client.delete_user("user-123", "auth.token")

        self.assertTrue(result)
        self.mock_client.delete.assert_called_once_with(
            "http://user-service:8000/api/v1/users/user-123",
            headers={"Authorization": "Bearer auth.token"},
        )

    async def test_delete_user_failure(self):
        mock_response = AsyncMock()
        mock_response.status_code = 404
        self.mock_client.delete.return_value = mock_response

        result = await self.client.delete_user("user-123", "auth.token")

        self.assertFalse(result)

    async def test_assign_role_success(self):
        mock_response = AsyncMock()
        mock_response.status_code = 200
        self.mock_client.post.return_value = mock_response

        result = await self.client.assign_role("user-123", "admin", "auth.token")

        self.assertTrue(result)
        self.mock_client.post.assert_called_once_with(
            "http://user-service:8000/api/v1/auth/assign-role",
            json={"user_id": "user-123", "role": "admin"},
            headers={"Authorization": "Bearer auth.token"},
        )

    async def test_assign_role_failure(self):
        mock_response = AsyncMock()
        mock_response.status_code = 403
        self.mock_client.post.return_value = mock_response

        result = await self.client.assign_role("user-123", "admin", "auth.token")

        self.assertFalse(result)
