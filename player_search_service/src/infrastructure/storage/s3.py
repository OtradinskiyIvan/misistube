import aiobotocore.session
from datetime import datetime, timedelta
from typing import Tuple
from .protocol import StoragePort

class S3StorageAdapter(StoragePort):
    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket: str
    ):
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.session = aiobotocore.session.get_session()
    
    async def generate_presigned_url(
        self, 
        object_key: str, 
        expires_in: int = 900  # 15 минут
    ) -> Tuple[str, datetime]:
        async with self.session.create_client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        ) as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": object_key},
                ExpiresIn=expires_in
            )
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            return url, expires_at