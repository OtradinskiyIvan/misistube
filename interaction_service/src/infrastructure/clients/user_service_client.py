from typing import Optional
from uuid import UUID

import httpx


class UserBrief:
    def __init__(self, id: UUID, username: str, avatar_url: Optional[str], status: str) -> None:
        self.id = id
        self.username = username
        self.avatar_url = avatar_url
        self.status = status


class UserServiceClient:
    def __init__(self, base_url: str, timeout: int = 10) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def get_brief(self, user_id: UUID) -> Optional[UserBrief]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(f"{self._base_url}/api/v1/users/{user_id}/brief")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()
            return UserBrief(
                id=UUID(data["id"]),
                username=data["username"],
                avatar_url=data.get("avatar_url"),
                status=data["status"],
            )

    async def get_batch_brief(self, user_ids: list[UUID]) -> list[UserBrief]:
        if not user_ids:
            return []
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                f"{self._base_url}/api/v1/users/batch",
                json={"ids": [str(uid) for uid in user_ids]},
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                UserBrief(
                    id=UUID(item["id"]),
                    username=item["username"],
                    avatar_url=item.get("avatar_url"),
                    status=item["status"],
                )
                for item in data
            ]

    async def follow(self, follower_id: UUID, following_id: UUID) -> bool:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                f"{self._base_url}/api/v1/users/{follower_id}/follow/{following_id}",
            )
            return resp.status_code == 200

    async def unfollow(self, follower_id: UUID, following_id: UUID) -> bool:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.delete(
                f"{self._base_url}/api/v1/users/{follower_id}/follow/{following_id}",
            )
            return resp.status_code == 204

    async def get_following(self, user_id: UUID) -> list[dict]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(
                f"{self._base_url}/api/v1/users/{user_id}/following",
            )
            if resp.status_code != 200:
                return []
            return resp.json()

    async def get_followers(self, user_id: UUID) -> list[dict]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(
                f"{self._base_url}/api/v1/users/{user_id}/followers",
            )
            if resp.status_code != 200:
                return []
            return resp.json()

    async def is_following(self, follower_id: UUID, following_id: UUID) -> bool:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.get(
                f"{self._base_url}/api/v1/users/{follower_id}/is-following/{following_id}",
            )
            if resp.status_code != 200:
                return False
            data = resp.json()
            return data.get("is_following", False)

    async def update_user_status(self, user_id: UUID, status: str) -> bool:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.put(
                f"{self._base_url}/api/v1/users/{user_id}",
                json={"status": status},
            )
            return resp.status_code == 200
