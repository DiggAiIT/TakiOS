"""File storage abstraction for MinIO/S3."""

import io

import boto3
from botocore.client import Config

from app.config import settings


def get_storage_client():
    """Create a MinIO/S3 client."""
    return boto3.client(
        "s3",
        endpoint_url=f"http://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version="s3v4"),
    )


async def upload_file(key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    """Upload a file to storage and return the key."""
    client = get_storage_client()
    client.put_object(
        Bucket=settings.minio_bucket,
        Key=key,
        Body=io.BytesIO(data),
        ContentLength=len(data),
        ContentType=content_type,
    )
    return key


async def delete_file(key: str) -> None:
    """Delete a file from storage."""
    client = get_storage_client()
    client.delete_object(Bucket=settings.minio_bucket, Key=key)


async def get_file_url(key: str, expires_in: int = 3600) -> str:
    """Generate a presigned URL for a stored file."""
    client = get_storage_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.minio_bucket, "Key": key},
        ExpiresIn=expires_in,
    )
