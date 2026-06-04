import httpx


class UserServiceClient:
    def __init__(self, base_url: str, timeout: int = 10) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def sync_user(self, jwt_token: str) -> bool:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                f"{self._base_url}/api/v1/auth/sync",
                json={"token": jwt_token},
            )
            return resp.status_code == 200
