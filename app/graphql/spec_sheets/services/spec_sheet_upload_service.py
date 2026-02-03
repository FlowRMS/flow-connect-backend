import io
import os
from uuid import uuid4

import httpx
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.files import File, FileType
from commons.s3.service import S3Service
from loguru import logger

from app.graphql.links.services.links_service import LinksService
from app.graphql.spec_sheets.strawberry.spec_sheet_input import CreateSpecSheetInput
from app.graphql.v2.files.repositories.file_repository import FileRepository

# S3 key prefix for spec sheet uploads
SPEC_SHEETS_S3_PREFIX = "spec-sheets"


class UploadResult:
    """Result of a spec sheet file upload."""

    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        file_url: str | None,
        file_size: int,
        s3_key: str | None,
        file_record: File | None,
    ) -> None:
        self.file_url = file_url
        self.file_size = file_size
        self.s3_key = s3_key
        self.file_record = file_record


class SpecSheetUploadService:
    """Service for handling spec sheet file uploads to S3."""

    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        s3_service: S3Service,
        file_repository: FileRepository,
        links_service: LinksService,
    ) -> None:
        self.s3_service = s3_service
        self.file_repository = file_repository
        self.links_service = links_service

    async def upload_spec_sheet(
        self,
        input_data: CreateSpecSheetInput,
    ) -> UploadResult:
        """
        Handle file upload for a spec sheet.

        Supports both direct file upload and URL-based upload.

        Args:
            input_data: Spec sheet creation data with file or URL

        Returns:
            UploadResult with file URL, size, S3 key, and File record
        """
        file_url: str | None = None
        file_size: int = 0
        s3_key: str | None = None

        if input_data.file and input_data.upload_source == "file":
            file_url, file_size, s3_key = await self._upload_from_file(input_data)
        elif input_data.upload_source == "url" and input_data.source_url:
            file_url, file_size, s3_key = await self._upload_from_url(input_data)

        # Create File record for /files integration
        file_record: File | None = None
        if s3_key and file_size > 0:
            file_record = await self._create_file_record(input_data, s3_key, file_size)

        return UploadResult(
            file_url=file_url,
            file_size=file_size,
            s3_key=s3_key,
            file_record=file_record,
        )

    async def _upload_from_file(
        self,
        input_data: CreateSpecSheetInput,
    ) -> tuple[str, int, str]:
        """Upload a file from direct upload."""
        if not input_data.file:
            raise ValueError("File is required for file upload")

        # Generate unique filename
        file_extension = os.path.splitext(input_data.file_name)[1] or ".pdf"
        unique_filename = f"{uuid4()}{file_extension}"
        s3_key = f"{SPEC_SHEETS_S3_PREFIX}/{unique_filename}"

        # Read file content
        content = await input_data.file.read()
        file_size = len(content)

        await self.s3_service.upload(
            key=s3_key,
            file_obj=io.BytesIO(content),
            ContentType="application/pdf",
        )

        # Generate presigned URL for access
        file_url = await self.s3_service.generate_presigned_url(key=s3_key)
        logger.info("Upload successful, presigned URL generated")

        return file_url, file_size, s3_key

    async def _upload_from_url(
        self,
        input_data: CreateSpecSheetInput,
    ) -> tuple[str, int, str]:
        """Download PDF from URL and upload to S3."""
        if not input_data.source_url:
            raise ValueError("Source URL is required for URL upload")

        logger.info(f"Downloading PDF from URL: {input_data.source_url}")

        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            response = await client.get(input_data.source_url)
            _ = response.raise_for_status()
            content = response.content
            file_size = len(content)

        # Generate unique filename
        file_extension = os.path.splitext(input_data.file_name)[1] or ".pdf"
        unique_filename = f"{uuid4()}{file_extension}"
        s3_key = f"{SPEC_SHEETS_S3_PREFIX}/{unique_filename}"

        # Upload to S3
        await self.s3_service.upload(
            key=s3_key,
            file_obj=io.BytesIO(content),
            ContentType="application/pdf",
        )

        # Generate presigned URL for access
        file_url = await self.s3_service.generate_presigned_url(key=s3_key)
        logger.info("URL upload successful, PDF stored in S3")

        return file_url, file_size, s3_key

    async def _create_file_record(
        self,
        input_data: CreateSpecSheetInput,
        s3_key: str,
        file_size: int,
    ) -> File:
        """Create a File record and link it to the Factory."""
        file_record = File(
            file_name=input_data.file_name,
            file_path=s3_key,
            file_size=file_size,
            file_type=FileType.PDF,
            folder_id=input_data.folder_id,
        )
        file_record = await self.file_repository.create(file_record)
        logger.info(f"Created File record {file_record.id} for spec sheet")

        # Link File to Factory so it appears in /files when browsing by Factory
        try:
            _ = await self.links_service.create_link(
                source_type=EntityType.FILE,
                source_id=file_record.id,
                target_type=EntityType.FACTORY,
                target_id=input_data.factory_id,
            )
            logger.info(
                f"Linked File {file_record.id} to Factory {input_data.factory_id}"
            )
        except Exception as e:
            logger.warning(f"Failed to create link relation: {e}")

        return file_record
