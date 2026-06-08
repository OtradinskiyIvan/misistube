import aiobotocore.session
from botocore.config import Config

class S3Client:
    def __init__(self, endpoint_url, access_key, secret_key, bucket_name, public_endpoint_url=None, thumbnail_bucket_name=None):
        self.endpoint_url = endpoint_url
        self.public_endpoint_url = public_endpoint_url or endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.thumbnail_bucket_name = thumbnail_bucket_name or bucket_name
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

    async def delete_file(self, key: str) -> None:
        async with self.session.create_client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=self.config,
        ) as client:
            await client.delete_object(Bucket=self.bucket_name, Key=key)

    async def get_file_stream(self, key: str, range_header: str = None) -> dict:
        async with self.session.create_client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=self.config,
        ) as client:
            kwargs = {"Bucket": self.bucket_name, "Key": key}
            if range_header:
                kwargs["Range"] = range_header
            response = await client.get_object(**kwargs)
            body = await response["Body"].read()
            return {
                "Body": body,
                "ContentLength": response["ContentLength"],
                "ContentType": response.get("ContentType", "video/mp4"),
                "ContentRange": response.get("ContentRange"),
            }

    async def upload_thumbnail_file(self, key: str, data: bytes, content_type: str = "image/jpeg") -> str:
        async with self.session.create_client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=self.config,
        ) as client:
            await client.put_object(
                Bucket=self.thumbnail_bucket_name,
                Key=key,
                Body=data,
                ContentType=content_type
            )
        return f"{self.endpoint_url}/{self.thumbnail_bucket_name}/{key}"

    async def delete_thumbnail_file(self, key: str) -> None:
        async with self.session.create_client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=self.config,
        ) as client:
            await client.delete_object(Bucket=self.thumbnail_bucket_name, Key=key)

    async def get_thumbnail_stream(self, key: str) -> dict:
        async with self.session.create_client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=self.config,
        ) as client:
            response = await client.get_object(Bucket=self.thumbnail_bucket_name, Key=key)
            body = await response["Body"].read()
            return {
                "Body": body,
                "ContentLength": response["ContentLength"],
                "ContentType": response.get("ContentType", "image/jpeg"),
            }

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
            if self.public_endpoint_url != self.endpoint_url:
                url = url.replace(self.endpoint_url, self.public_endpoint_url)
            return url
