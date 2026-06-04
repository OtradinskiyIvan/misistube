from datetime import datetime, timedelta

import aiobotocore.session
from aiobotocore.session import AioSession

from src.core.config import get_settings

from .protocol import StoragePort


class S3StorageAdapter(StoragePort):
    """MinIO/S3 адаптер через aiobotocore"""

    def __init__(
        self,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
    ):
        settings = get_settings()
        self.endpoint_url = endpoint_url or settings.S3_ENDPOINT_URL
        self.access_key = access_key or settings.S3_ACCESS_KEY
        self.secret_key = secret_key or settings.S3_SECRET_KEY
        self.session: AioSession = aiobotocore.session.get_session()

    async def generate_presigned_url(
        self,
        object_key: str,
        bucket: str,
        expires_in: int = 900
    ) -> tuple[str, datetime]:
        """Генерирует presigned GET URL"""
        async with self.session.create_client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        ) as client:
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
        async with self.session.create_client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        ) as client:
            # Проверяем существование бакета
            try:
                await client.head_bucket(Bucket=bucket)
            except Exception:
                await client.create_bucket(Bucket=bucket)

            await client.put_object(
                Bucket=bucket,
                Key=object_key,
                Body=file_bytes,
                ContentType=content_type
            )
