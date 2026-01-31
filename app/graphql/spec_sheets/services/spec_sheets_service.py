import io
import os
from uuid import UUID, uuid4

import httpx
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.spec_sheets.spec_sheet_model import SpecSheet
from commons.db.v6.files import File, FileType
from commons.s3.service import S3Service
from loguru import logger

from app.graphql.links.services.links_service import LinksService
from app.graphql.spec_sheets.repositories.spec_sheets_repository import (
    SpecSheetsRepository,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_input import (
    CreateSpecSheetInput,
    UpdateSpecSheetInput,
)
from app.graphql.v2.files.repositories.file_repository import FileRepository

# S3 key prefix for spec sheet uploads
SPEC_SHEETS_S3_PREFIX = "spec-sheets"


class SpecSheetsService:
    """Service for SpecSheets business logic."""

    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        repository: SpecSheetsRepository,
        s3_service: S3Service,
        file_repository: FileRepository,
        links_service: LinksService,
    ) -> None:
        """
        Initialize the SpecSheets service.

        Args:
            repository: SpecSheets repository instance
            s3_service: S3 service for file uploads
            file_repository: File repository for /files integration
            links_service: Links service for entity relationships
        """
        self.repository = repository
        self.s3_service = s3_service
        self.file_repository = file_repository
        self.links_service = links_service

    async def create_spec_sheet(self, input_data: CreateSpecSheetInput) -> SpecSheet:
        """
        Create a new spec sheet.

        Also creates a File record in /files and links it to the Factory,
        so the spec sheet appears when browsing files by Factory entity.

        Args:
            input_data: Spec sheet creation data

        Returns:
            Created SpecSheet model
        """
        # Handle file upload if provided
        file_url: str | None = None
        file_size: int = 0
        s3_key: str | None = None

        if input_data.file and input_data.upload_source == "file":
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
            file_url = await self.s3_service.generate_presigned_url(
                key=s3_key,
            )

            logger.info("Upload successful, presigned URL generated")
        elif input_data.upload_source == "url" and input_data.source_url:
            # Download PDF from URL and upload to S3
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
            file_url = await self.s3_service.generate_presigned_url(
                key=s3_key,
            )

            logger.info("URL upload successful, PDF stored in S3")

        # Use display_name if provided, otherwise use file_name
        display_name = input_data.display_name or input_data.file_name

        # Create File record for /files integration
        file_record: File | None = None
        if s3_key and file_size > 0:
            file_record = File(
                file_name=input_data.file_name,
                file_path=s3_key,
                file_size=file_size,
                file_type=FileType.PDF,
                folder_id=input_data.folder_id,  # Set folder using pyfiles.folders
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

        spec_sheet = SpecSheet(
            factory_id=input_data.factory_id,
            file_name=input_data.file_name,
            display_name=display_name,
            upload_source=input_data.upload_source,
            source_url=input_data.source_url,
            file_url=file_url or "",
            file_size=file_size or 0,
            page_count=input_data.page_count,
            categories=input_data.categories,
            tags=input_data.tags,
            needs_review=input_data.needs_review,
            published=input_data.published,
            usage_count=0,
            highlight_count=0,
            file_id=file_record.id if file_record else None,
        )

        return await self.repository.create(spec_sheet)

    async def update_spec_sheet(
        self, spec_sheet_id: UUID, input_data: UpdateSpecSheetInput
    ) -> SpecSheet:
        """
        Update an existing spec sheet.

        Args:
            spec_sheet_id: UUID of the spec sheet to update
            input_data: Update data

        Returns:
            Updated SpecSheet model

        Raises:
            ValueError: If spec sheet not found
        """
        spec_sheet = await self.repository.get_by_id(spec_sheet_id)
        if not spec_sheet:
            raise ValueError(f"SpecSheet with id {spec_sheet_id} not found")

        # Update fields if provided (using optional_field to handle UNSET)
        display_name = input_data.optional_field(input_data.display_name)
        if display_name is not None:
            spec_sheet.display_name = display_name

        categories = input_data.optional_field(input_data.categories)
        if categories is not None:
            spec_sheet.categories = categories

        tags = input_data.optional_field(input_data.tags)
        if tags is not None:
            spec_sheet.tags = tags

        needs_review = input_data.optional_field(input_data.needs_review)
        if needs_review is not None:
            spec_sheet.needs_review = needs_review

        published = input_data.optional_field(input_data.published)
        if published is not None:
            spec_sheet.published = published

        return await self.repository.update(spec_sheet)

    async def delete_spec_sheet(self, spec_sheet_id: UUID) -> bool:
        """
        Delete a spec sheet.

        Also removes the linked File record and LinkRelation.

        Args:
            spec_sheet_id: UUID of the spec sheet to delete

        Returns:
            True if deleted successfully
        """
        # Get spec sheet to find linked file
        spec_sheet = await self.repository.get_by_id(spec_sheet_id)
        if not spec_sheet:
            return False

        # Delete linked File and LinkRelation if exists
        if spec_sheet.file_id:
            try:
                # Delete link relation first
                _ = await self.links_service.delete_link_by_entities(
                    source_type=EntityType.FILE,
                    source_id=spec_sheet.file_id,
                    target_type=EntityType.FACTORY,
                    target_id=spec_sheet.factory_id,
                )
            except Exception as e:
                logger.warning(f"Failed to delete link relation: {e}")

            try:
                # Delete file record
                _ = await self.file_repository.delete(spec_sheet.file_id)
            except Exception as e:
                logger.warning(f"Failed to delete file record: {e}")

        return await self.repository.delete(spec_sheet_id)

    async def get_spec_sheet(self, spec_sheet_id: UUID) -> SpecSheet | None:
        """
        Get a spec sheet by ID.

        Args:
            spec_sheet_id: UUID of the spec sheet

        Returns:
            SpecSheet model or None if not found
        """
        return await self.repository.get_by_id(spec_sheet_id)

    async def get_spec_sheets_by_factory(
        self, factory_id: UUID, published_only: bool = True
    ) -> list[SpecSheet]:
        """
        Get all spec sheets for a factory.

        Args:
            factory_id: UUID of the factory
            published_only: Filter only published spec sheets

        Returns:
            List of SpecSheet models
        """
        return await self.repository.find_by_factory(factory_id, published_only)

    async def search_spec_sheets(
        self,
        search_term: str = "",
        factory_id: UUID | None = None,
        categories: list[str] | None = None,
        published_only: bool = True,
        limit: int = 50,
    ) -> list[SpecSheet]:
        """
        Search spec sheets.

        Args:
            search_term: Search term for display_name and file_name
            factory_id: Optional factory filter
            categories: Optional categories filter
            published_only: Filter only published spec sheets
            limit: Maximum number of results

        Returns:
            List of matching SpecSheet models
        """
        return await self.repository.search_spec_sheets(
            search_term, factory_id, categories, published_only, limit
        )

    async def increment_usage(self, spec_sheet_id: UUID) -> None:
        """
        Increment usage count for a spec sheet.

        Args:
            spec_sheet_id: UUID of the spec sheet
        """
        await self.repository.increment_usage_count(spec_sheet_id)

    async def move_spec_sheet_to_folder(
        self,
        spec_sheet_id: UUID,
        folder_id: UUID | None,
    ) -> SpecSheet | None:
        """
        Move a spec sheet to a different folder.

        Updates the File.folder_id to move the spec sheet.

        Args:
            spec_sheet_id: UUID of the spec sheet
            folder_id: UUID of the target folder (None for root/no folder)

        Returns:
            Updated SpecSheet or None if not found
        """
        return await self.repository.move_to_folder(spec_sheet_id, folder_id)

    async def get_spec_sheets_by_folder(
        self,
        factory_id: UUID,
        folder_id: UUID | None,
        published_only: bool = True,
    ) -> list[SpecSheet]:
        """
        Get all spec sheets in a specific folder.

        Args:
            factory_id: UUID of the factory
            folder_id: UUID of the folder (None for root/unassigned)
            published_only: Filter only published spec sheets

        Returns:
            List of SpecSheet models in the folder
        """
        return await self.repository.find_by_folder(
            factory_id, folder_id, published_only
        )
