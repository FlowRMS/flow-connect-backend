from uuid import UUID

from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.spec_sheets.spec_sheet_model import SpecSheet
from commons.s3.service import S3Service
from loguru import logger

from app.graphql.links.services.links_service import LinksService
from app.graphql.spec_sheets.repositories.spec_sheets_repository import (
    SpecSheetsRepository,
)
from app.graphql.spec_sheets.services.spec_sheet_upload_service import (
    SpecSheetUploadService,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_input import (
    CreateSpecSheetInput,
    UpdateSpecSheetInput,
)
from app.graphql.v2.files.repositories.file_repository import FileRepository


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
        self.links_service = links_service
        self.file_repository = file_repository
        self._upload_service = SpecSheetUploadService(
            s3_service, file_repository, links_service
        )

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
        # Handle file upload via the upload service
        upload_result = await self._upload_service.upload_spec_sheet(input_data)

        # Use display_name if provided, otherwise use file_name
        display_name = input_data.display_name or input_data.file_name

        spec_sheet = SpecSheet(
            factory_id=input_data.factory_id,
            file_name=input_data.file_name,
            display_name=display_name,
            upload_source=input_data.upload_source,
            source_url=input_data.source_url,
            file_url=upload_result.file_url or "",
            file_size=upload_result.file_size or 0,
            page_count=input_data.page_count,
            categories=input_data.categories,
            tags=input_data.tags,
            needs_review=input_data.needs_review,
            published=input_data.published,
            usage_count=0,
            highlight_count=0,
            file_id=upload_result.file_record.id if upload_result.file_record else None,
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
        spec_sheet = await self.repository.get_by_id(spec_sheet_id)
        if not spec_sheet:
            return False

        if spec_sheet.file_id:
            try:
                _ = await self.links_service.delete_link_by_entities(
                    source_type=EntityType.FILE,
                    source_id=spec_sheet.file_id,
                    target_type=EntityType.FACTORY,
                    target_id=spec_sheet.factory_id,
                )
            except Exception as e:
                logger.warning(f"Failed to delete link relation: {e}")

            try:
                _ = await self.file_repository.delete(spec_sheet.file_id)
            except Exception as e:
                logger.warning(f"Failed to delete file record: {e}")

        return await self.repository.delete(spec_sheet_id)

    async def get_spec_sheet(self, spec_sheet_id: UUID) -> SpecSheet | None:
        """Get a spec sheet by ID."""
        return await self.repository.get_by_id(spec_sheet_id)

    async def get_spec_sheets_by_factory(
        self, factory_id: UUID, published_only: bool = True
    ) -> list[SpecSheet]:
        """Get all spec sheets for a factory."""
        return await self.repository.find_by_factory(factory_id, published_only)

    async def search_spec_sheets(
        self,
        search_term: str = "",
        factory_id: UUID | None = None,
        categories: list[str] | None = None,
        published_only: bool = True,
        limit: int = 50,
    ) -> list[SpecSheet]:
        """Search spec sheets."""
        return await self.repository.search_spec_sheets(
            search_term, factory_id, categories, published_only, limit
        )

    async def increment_usage(self, spec_sheet_id: UUID) -> None:
        """Increment usage count for a spec sheet."""
        await self.repository.increment_usage_count(spec_sheet_id)

    async def move_spec_sheet_to_folder(
        self, spec_sheet_id: UUID, folder_id: UUID | None
    ) -> SpecSheet | None:
        """Move a spec sheet to a different folder."""
        return await self.repository.move_to_folder(spec_sheet_id, folder_id)

    async def get_spec_sheets_by_folder(
        self, factory_id: UUID, folder_id: UUID | None, published_only: bool = True
    ) -> list[SpecSheet]:
        """Get all spec sheets in a specific folder."""
        return await self.repository.find_by_folder(
            factory_id, folder_id, published_only
        )
