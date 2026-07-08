import asyncio
import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass
class UserInfo:
    """Информация о пользователе из User сервиса"""

    user_id: str
    username: str
    email: str | None = None
    channel_url: str | None = None


class UserServiceClient:
    """Клиент для получения информации о пользователях из User сервиса"""

    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url.rstrip("/")
        self.timeout = 5.0

    async def get_user_info(self, user_id: str) -> UserInfo | None:
        """
        Получает информацию о пользователе по ID

        Args:
            user_id: UUID пользователя

        Returns:
            UserInfo или None, если пользователь не найден
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/users/{user_id}")

                if response.status_code == 404:
                    logger.warning("User not found: %s", user_id)
                    return None

                response.raise_for_status()
                data = response.json()

                username = data.get("username")
                if not username:
                    logger.error("Username missing in user service response for %s", user_id)
                    return None

                return UserInfo(
                    user_id=user_id,
                    username=username,
                    email=data.get("email"),
                    channel_url=data.get("channel_url", f"/channel/{user_id}"),
                )

        except httpx.TimeoutException:
            logger.error("Timeout while fetching user info for %s", user_id)
            return None
        except httpx.HTTPError as e:
            logger.error("HTTP error while fetching user info for %s: %s", user_id, e)
            return None
        except Exception as e:
            logger.error("Unexpected error while fetching user info for %s: %s", user_id, e)
            return None

    async def get_username(self, user_id: str) -> str | None:
        """
        Получает только username пользователя по ID.
        Удобно для обогащения списков видео.

        Args:
            user_id: UUID пользователя

        Returns:
            username или None, если не удалось получить
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/users/{user_id}")

                if response.status_code == 404:
                    logger.warning("User not found: %s", user_id)
                    return None

                if response.status_code != 200:
                    logger.warning("Failed to fetch user %s: %s", user_id, response.status_code)
                    return None

                data = response.json()
                return data.get("username")

        except httpx.TimeoutException:
            logger.warning("Timeout while fetching username for %s", user_id)
            return None
        except Exception as e:
            logger.warning("Error fetching username for %s: %s", user_id, e)
            return None

    async def get_usernames_batch(self, user_ids: list[str]) -> dict[str, str]:
        """
        Получает username для списка user_id параллельно.

        Args:
            user_ids: список UUID пользователей

        Returns:
            Словарь {user_id: username}.
            Если username не получен — user_id не будет в словаре.
        """
        if not user_ids:
            return {}

        tasks = [self.get_username(uid) for uid in user_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        usernames = {}
        for user_id, result in zip(user_ids, results, strict=True):
            if isinstance(result, str):
                usernames[user_id] = result
            elif isinstance(result, Exception):
                logger.warning("Batch fetch failed for %s: %s", user_id, result)

        return usernames

    async def get_user_avatar(self, user_id: str) -> str | None:
        """
        Получает URL аватарки пользователя через /profile эндпоинт.

        Args:
            user_id: UUID пользователя

        Returns:
            URL аватарки или None, если не удалось получить
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/users/{user_id}/profile")

                if response.status_code == 404:
                    logger.warning("User profile not found: %s", user_id)
                    return None

                if response.status_code != 200:
                    logger.warning(
                        "Failed to fetch user profile %s: %s", user_id, response.status_code
                    )
                    return None

                data = response.json()
                return data.get("avatar_url")

        except httpx.TimeoutException:
            logger.warning("Timeout while fetching avatar for %s", user_id)
            return None
        except Exception as e:
            logger.warning("Error fetching avatar for %s: %s", user_id, e)
            return None

    async def get_avatars_batch(self, user_ids: list[str]) -> dict[str, str | None]:
        """
        Получает аватарки для списка user_id параллельно.
        """
        if not user_ids:
            return {}

        tasks = [self.get_user_avatar(uid) for uid in user_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        avatars = {}
        for user_id, result in zip(user_ids, results, strict=True):
            if isinstance(result, str):
                avatars[user_id] = result
            elif isinstance(result, Exception):
                logger.warning("Batch avatar fetch failed for %s: %s", user_id, result)
                avatars[user_id] = None
            else:
                avatars[user_id] = None

        return avatars
