import httpx


class UserServiceClient:
    def __init__(self, base_url: str, internal_api_key: str = "", timeout: int = 10) -> None:
        self._base_url = base_url.rstrip("/")
        self._internal_api_key = internal_api_key
        self._timeout = timeout

    async def sync_user(self, jwt_token: str) -> bool:
        headers = {"Content-Type": "application/json"}
        if self._internal_api_key:
            headers["X-API-Key"] = self._internal_api_key
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                f"{self._base_url}/api/v1/auth/sync",
                json={"token": jwt_token},
                headers=headers,
            )
            return resp.status_code == 200

    async def delete_user(self, user_id: str, auth_token: str) -> bool:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.delete(
                f"{self._base_url}/api/v1/users/{user_id}",
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            return resp.status_code == 204

    async def assign_role(self, user_id: str, role: str, auth_token: str) -> bool:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                f"{self._base_url}/api/v1/auth/assign-role",
                json={"user_id": user_id, "role": role},
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            return resp.status_code == 200
