import logging
from datetime import UTC, datetime, timedelta

import aiobotocore.session
from aiobotocore.session import AioSession

from src.core.config import get_settings

from .protocol import StoragePort

logger = logging.getLogger(__name__)


class S3StorageAdapter(StoragePort):
    """MinIO/S3 адаптер через aiobotocore с переиспользованием клиента"""

    def __init__(
        self,
        endpoint_url: str | None = None,
        public_endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
    ):
        settings = get_settings()
        self.endpoint_url = endpoint_url or settings.S3_ENDPOINT_URL
        self.public_endpoint_url = public_endpoint_url or settings.S3_PUBLIC_ENDPOINT_URL
        self.access_key = access_key or settings.S3_ACCESS_KEY.get_secret_value()
        self.secret_key = secret_key or settings.S3_SECRET_KEY.get_secret_value()

        self.session: AioSession = aiobotocore.session.get_session()
        self._client = None
        self._client_context = None

    async def _get_client(self):
        """Ленивая инициализация клиента (входим в контекст один раз)"""
        if self._client is None:
            self._client_context = self.session.create_client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
            )
            self._client = await self._client_context.__aenter__()
        return self._client

    async def close(self):
        """Корректное закрытие клиента"""
        if self._client_context is not None:
            await self._client_context.__aexit__(None, None, None)
            self._client = None
            self._client_context = None

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
        if self.public_endpoint_url:
            url = url.replace(self.endpoint_url, self.public_endpoint_url)
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
        return url, expires_at

    async def upload_file(
        self,
        file_bytes: bytes,
        object_key: str,
        bucket: str,
        content_type: str = "application/octet-stream"
    ) -> None:
        """
        ЗАПРЕЩЕНО: Этот сервис имеет права только на чтение.
        Для загрузки файлов используйте creation_service.
        """
        raise NotImplementedError(
            "Этот сервис (player_search) имеет права только на чтение. "
            "Загрузка файлов запрещена. Используйте video_upload_service."
        )
