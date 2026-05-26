from typing import Protocol
from datetime import datetime
from abc import abstractmethod

class StoragePort(Protocol):
    @abstractmethod
    async def generate_presigned_url(
        self, 
        object_key: str, 
        expires_in: int = 900
    ) -> tuple[str, datetime]:
        """Генерирует presigned URL для HLS-файла"""
        pass