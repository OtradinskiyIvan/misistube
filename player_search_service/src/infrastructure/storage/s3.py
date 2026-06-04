import logging
from datetime import datetime, timedelta

import aiobotocore.session
from aiobotocore.session import AioSession
from botocore.exceptions import ClientError

from src.core.config import get_settings
from .protocol import StoragePort

logger = logging.getLogger(__name__)


class S3StorageAdapter(StoragePort):
    """MinIO/S3 адаптер через aiobotocore с переиспользованием клиента"""

    def __init__(
        self,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
    ):
        settings = get_settings()
        self.endpoint_url = endpoint_url or settings.S3_ENDPOINT_URL
        self.access_key = access_key or settings.S3_ACCESS_KEY.get_secret_value()
        self.secret_key = secret_key or settings.S3_SECRET_KEY.get_secret_value()
        
        self.session: AioSession = aiobotocore.session.get_session()
        self._client = None  # 🔹 P1: Кэш для клиента

    async def _get_client(self):
        """Ленивая инициализация клиента (создаётся только один раз)"""
        if self._client is None:
            self._client = self.session.create_client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
        return self._client

    async def close(self):
        """Корректное закрытие клиента при завершении работы приложения"""
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def generate_presigned_url(
        self,
        object_key: str,
        bucket: str,
        expires_in: int = 900
    ) -> tuple[str, datetime]:
        """Генерирует presigned GET URL"""
        client = await self._get_client()
        
        url = await client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket,
                "Key": object_key,
            },
            ExpiresIn=expires_in
        )
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        return url, expires_at

    async def upload_file(
        self,
        file_bytes: bytes,
        object_key: str,
        bucket: str,
        content_type: str = "application/octet-stream"
    ) -> None:
        """Загружает файл в бакет"""
        client = await self._get_client()
        
        try:
            await client.head_bucket(Bucket=bucket)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code in ("404", "403", "NoSuchBucket"):
                logger.info(f"Bucket '{bucket}' not found, creating...")
                await client.create_bucket(Bucket=bucket)
            else:
                logger.error(f"Error checking bucket '{bucket}': {e}")
                raise

        await client.put_object(
            Bucket=bucket,
            Key=object_key,
            Body=file_bytes,
            ContentType=content_type
        )