import logging
from typing import Optional
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class UserInfo:
    """Информация о пользователе из User сервиса"""
    user_id: str
    username: str
    email: Optional[str] = None
    channel_url: Optional[str] = None


class UserServiceClient:
    """Клиент для получения информации о пользователях из User сервиса"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url.rstrip("/")
        self.timeout = 5.0
    
    async def get_user_info(self, user_id: str) -> Optional[UserInfo]:
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
                    channel_url=data.get("channel_url", f"/channel/{user_id}")
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