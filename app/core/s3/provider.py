from collections.abc import Iterable
from typing import Any

import aioinject
from commons.auth import AuthInfo
from commons.s3.service import S3Service

from app.core.s3.settings import S3Settings


def create_s3_service(settings: S3Settings, auth_info: AuthInfo) -> S3Service:
    return S3Service(
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        endpoint_url=settings.aws_endpoint_url,
        bucket_name=settings.aws_bucket_name,
        tenant_name=auth_info.tenant_name,
    )


providers: Iterable[aioinject.Provider[Any]] = [
    aioinject.Scoped(create_s3_service),
]
