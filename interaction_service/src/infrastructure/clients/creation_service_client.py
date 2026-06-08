from typing import Optional
from uuid import UUID

import httpx


class CreationServiceClient:
    def __init__(self, base_url: str, timeout: int = 10) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def get_video_owner(self, video_id: UUID) -> Optional[UUID]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(f"{self._base_url}/videos/{video_id}/owner")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
            return UUID(data["user_id"])
