from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.infrastructure.user_service.client import UserServiceClient


@pytest.fixture
def client():
    return UserServiceClient(base_url="http://test-user:8002")


class TestUserServiceClient:
    async def _mock_get(self, status_code: int, json_data: dict | None = None):
        """Helper to create a mock for httpx.AsyncClient.get"""
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data or {}
        return mock_response

    # ─── get_user_info ────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_get_user_info_success(self, client):
        mock_response = await self._mock_get(200, {"username": "john", "email": "john@test.com"})

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_httpx.return_value.__aenter__.return_value.get.return_value = mock_response
            result = await client.get_user_info("user-1")

        assert result is not None
        assert result.user_id == "user-1"
        assert result.username == "john"
        assert result.email == "john@test.com"
        assert result.channel_url == "/channel/user-1"

    @pytest.mark.asyncio
    async def test_get_user_info_404(self, client):
        mock_response = await self._mock_get(404)

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_httpx.return_value.__aenter__.return_value.get.return_value = mock_response
            result = await client.get_user_info("user-404")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_info_no_username(self, client):
        mock_response = await self._mock_get(200, {"email": "no@name.com"})

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_httpx.return_value.__aenter__.return_value.get.return_value = mock_response
            result = await client.get_user_info("no-username")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_info_timeout(self, client):
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_httpx.return_value.__aenter__.return_value.get.side_effect = (
                httpx.TimeoutException("timeout")
            )
            result = await client.get_user_info("timeout-user")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_info_http_error(self, client):
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_httpx.return_value.__aenter__.return_value.get.side_effect = (
                httpx.HTTPStatusError("500 error", request=AsyncMock(), response=AsyncMock())
            )
            result = await client.get_user_info("err-user")

        assert result is None

    # ─── get_username ──────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_get_username_success(self, client):
        mock_response = await self._mock_get(200, {"username": "alice"})

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_httpx.return_value.__aenter__.return_value.get.return_value = mock_response
            result = await client.get_username("alice-id")

        assert result == "alice"

    @pytest.mark.asyncio
    async def test_get_username_404(self, client):
        mock_response = await self._mock_get(404)

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_httpx.return_value.__aenter__.return_value.get.return_value = mock_response
            result = await client.get_username("missing")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_username_not_200(self, client):
        mock_response = await self._mock_get(503)

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_httpx.return_value.__aenter__.return_value.get.return_value = mock_response
            result = await client.get_username("down-user")

        assert result is None

    # ─── get_usernames_batch ───────────────────────────────────

    @pytest.mark.asyncio
    async def test_get_usernames_batch_empty(self, client):
        result = await client.get_usernames_batch([])
        assert result == {}

    @pytest.mark.asyncio
    async def test_get_usernames_batch_success(self, client):
        async def mock_get_username(uid):
            return {"a": "Alice", "b": "Bob"}.get(uid)

        with patch.object(client, "get_username", side_effect=mock_get_username):
            result = await client.get_usernames_batch(["a", "b"])

        assert result == {"a": "Alice", "b": "Bob"}

    @pytest.mark.asyncio
    async def test_get_usernames_batch_partial_failure(self, client):
        async def mock_get_username(uid):
            if uid == "a":
                return "Alice"
            raise ValueError("fail")

        with patch.object(client, "get_username", side_effect=mock_get_username):
            result = await client.get_usernames_batch(["a", "b"])

        assert result == {"a": "Alice"}

    # ─── get_user_avatar ───────────────────────────────────────

    @pytest.mark.asyncio
    async def test_get_user_avatar_success(self, client):
        mock_response = await self._mock_get(200, {"avatar_url": "https://av.at/test.jpg"})

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_httpx.return_value.__aenter__.return_value.get.return_value = mock_response
            result = await client.get_user_avatar("avatar-user")

        assert result == "https://av.at/test.jpg"

    @pytest.mark.asyncio
    async def test_get_user_avatar_404(self, client):
        mock_response = await self._mock_get(404)

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_httpx.return_value.__aenter__.return_value.get.return_value = mock_response
            result = await client.get_user_avatar("no-avatar")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_avatar_not_200(self, client):
        mock_response = await self._mock_get(500)

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_httpx.return_value.__aenter__.return_value.get.return_value = mock_response
            result = await client.get_user_avatar("err-avatar")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_avatar_timeout(self, client):
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_httpx.return_value.__aenter__.return_value.get.side_effect = (
                httpx.TimeoutException("timeout")
            )
            result = await client.get_user_avatar("timeout-av")

        assert result is None

    # ─── get_avatars_batch ─────────────────────────────────────

    @pytest.mark.asyncio
    async def test_get_avatars_batch_empty(self, client):
        result = await client.get_avatars_batch([])
        assert result == {}

    @pytest.mark.asyncio
    async def test_get_avatars_batch_success(self, client):
        async def mock_get_avatar(uid):
            return {"x": "https://av.at/x.jpg", "y": "https://av.at/y.jpg"}.get(uid)

        with patch.object(client, "get_user_avatar", side_effect=mock_get_avatar):
            result = await client.get_avatars_batch(["x", "y"])

        assert result == {"x": "https://av.at/x.jpg", "y": "https://av.at/y.jpg"}

    @pytest.mark.asyncio
    async def test_get_avatars_batch_with_exception(self, client):
        async def mock_get_avatar(uid):
            if uid == "x":
                return "https://av.at/x.jpg"
            raise ValueError("fail")

        with patch.object(client, "get_user_avatar", side_effect=mock_get_avatar):
            result = await client.get_avatars_batch(["x", "y"])

        assert result == {"x": "https://av.at/x.jpg", "y": None}
