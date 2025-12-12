"""S3 service provider for dependency injection."""

from collections.abc import Iterable
from typing import Any

import aioinject

from app.core.config.s3_settings import S3Settings
from commons.s3.service import S3Service


def create_s3_service(settings: S3Settings) -> S3Service:
    """Create S3Service instance from settings."""
    return S3Service(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        endpoint_url=settings.aws_endpoint_url,
        bucket_name=settings.aws_bucket_name,
    )


providers: Iterable[aioinject.Provider[Any]] = [
    aioinject.Singleton(create_s3_service),
]
