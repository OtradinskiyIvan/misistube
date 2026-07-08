from abc import abstractmethod
from datetime import datetime
from typing import Protocol


class StoragePort(Protocol):
    """Интерфейс объектного хранилища (S3/MinIO)"""

    @abstractmethod
    async def generate_presigned_url(
        self, object_key: str, bucket: str, expires_in: int = 900
    ) -> tuple[str, datetime]:
        """
        Генерирует presigned URL для доступа к объекту
        Args:
            object_key: Ключ объекта (путь внутри бакета)
            bucket: Имя бакета
            expires_in: Время жизни ссылки в секундах
        Returns:
            Tuple[URL, expiration_datetime]
        """
        pass

    @abstractmethod
    async def upload_file(
        self,
        file_bytes: bytes,
        object_key: str,
        bucket: str,
        content_type: str = "application/octet-stream",
    ) -> None:
        """Загрузить файл в хранилище"""
        pass
