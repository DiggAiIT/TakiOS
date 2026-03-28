import aioboto3

from app.config import settings

class MinioService:
    def __init__(self):
        self.session = aioboto3.Session()
        self.bucket = settings.minio_bucket
        self.endpoint_url = f"http://{settings.minio_endpoint}"
        
    async def get_presigned_upload_url(self, object_name: str, expiration: int = 3600):
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key
        ) as s3:
            url = await s3.generate_presigned_url(
                'put_object',
                Params={'Bucket': self.bucket, 'Key': object_name},
                ExpiresIn=expiration
            )
            return url

    async def get_presigned_download_url(self, object_name: str, expiration: int = 3600):
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key
        ) as s3:
            url = await s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_name},
                ExpiresIn=expiration
            )
            return url
