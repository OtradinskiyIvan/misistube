import aiobotocore.session
from botocore.config import Config

class S3Client:
    def __init__(self, endpoint_url, access_key, secret_key, bucket_name):
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.session = aiobotocore.session.get_session()
        self.config = Config(
            signature_version='s3v4',
            read_timeout=300,
            connect_timeout=60
        )

    async def upload_file(self, key: str, data: bytes, content_type: str = "video/mp4") -> str:
        async with self.session.create_client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=self.config,
        ) as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
                ContentType=content_type
            )
        return f"{self.endpoint_url}/{self.bucket_name}/{key}"

    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        async with self.session.create_client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=self.config,
        ) as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires_in,
            )
            return url
