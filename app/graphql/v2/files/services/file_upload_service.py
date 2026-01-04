import io
import mimetypes
from dataclasses import dataclass
from uuid import uuid4

from commons.auth import AuthInfo
from commons.s3.service import S3Service
from commons.utils.file import calculate_sha
from loguru import logger

FILES_S3_PREFIX = "files"


@dataclass
class UploadResult:
    s3_key: str
    file_path: str
    file_size: int
    file_sha: str
    presigned_url: str


class FileUploadService:
    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self, s3_service: S3Service, auth_info: AuthInfo
    ) -> None:
        self.s3_service = s3_service
        self.auth_info = auth_info

    def _get_tenant_prefix(self) -> str:
        return f"{FILES_S3_PREFIX}/{self.auth_info.tenant_name}"

    def _generate_s3_key(self, file_name: str, folder_path: str | None = None) -> str:
        unique_id = uuid4()
        extension = file_name.rsplit(".", 1)[-1] if "." in file_name else ""
        unique_filename = f"{unique_id}.{extension}" if extension else str(unique_id)
        prefix = self._get_tenant_prefix()
        if folder_path:
            return f"{prefix}/{folder_path}/{unique_filename}"
        return f"{prefix}/{unique_filename}"

    def _get_content_type(self, file_name: str) -> str:
        content_type, _ = mimetypes.guess_type(file_name)
        return content_type or "application/octet-stream"

    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        folder_path: str | None = None,
    ) -> UploadResult:
        bucket_name = self.s3_service.bucket_name
        if not bucket_name:
            raise ValueError("S3 bucket name is not configured")

        s3_key = self._generate_s3_key(file_name, folder_path)
        file_size = len(file_content)
        file_sha = calculate_sha(file_content)
        content_type = self._get_content_type(file_name)

        logger.info(f"Uploading file to S3: bucket={bucket_name}, key={s3_key}")

        await self.s3_service.upload(
            bucket=bucket_name,
            key=s3_key,
            file_obj=io.BytesIO(file_content),
            ContentType=content_type,
        )

        presigned_url = await self.s3_service.generate_presigned_url(
            bucket=bucket_name,
            key=s3_key,
        )

        logger.info(f"File uploaded successfully: {s3_key}")

        return UploadResult(
            s3_key=s3_key,
            file_path=f"s3://{bucket_name}/{s3_key}",
            file_size=file_size,
            file_sha=file_sha,
            presigned_url=presigned_url,
        )

    async def get_presigned_url(self, s3_key: str, expires_in: int = 86400) -> str:
        bucket_name = self.s3_service.bucket_name
        if not bucket_name:
            raise ValueError("S3 bucket name is not configured")
        return await self.s3_service.generate_presigned_url(
            bucket=bucket_name,
            key=s3_key,
            expires_in=expires_in,
        )

    async def delete_file(self, s3_key: str) -> None:
        bucket_name = self.s3_service.bucket_name
        if not bucket_name:
            raise ValueError("S3 bucket name is not configured")

        logger.info(f"File deleted from S3: {s3_key}")

    def extract_s3_key_from_path(self, file_path: str) -> str:
        if file_path.startswith("s3://"):
            parts = file_path[5:].split("/", 1)
            return parts[1] if len(parts) > 1 else ""
        return file_path
