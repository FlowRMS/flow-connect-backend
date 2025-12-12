"""Service layer for SpecSheets business logic."""

import os
from pathlib import Path
from uuid import UUID, uuid4

import aiofiles

from app.graphql.spec_sheets.models.spec_sheet_model import SpecSheet
from app.graphql.spec_sheets.repositories.spec_sheets_repository import (
    SpecSheetsRepository,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_input import (
    CreateSpecSheetInput,
    UpdateSpecSheetInput,
)

# Define uploads directory
UPLOADS_DIR = Path(__file__).parent.parent.parent.parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


class SpecSheetsService:
    """Service for SpecSheets business logic."""

    def __init__(self, repository: SpecSheetsRepository) -> None:
        """
        Initialize the SpecSheets service.

        Args:
            repository: SpecSheets repository instance
        """
        self.repository = repository

    async def create_spec_sheet(self, input_data: CreateSpecSheetInput) -> SpecSheet:
        """
        Create a new spec sheet.

        Args:
            input_data: Spec sheet creation data

        Returns:
            Created SpecSheet model
        """
        # Handle file upload if provided
        file_url = input_data.file_url
        file_size = input_data.file_size

        if input_data.file and input_data.upload_source == 'file':
            # Generate unique filename
            file_extension = os.path.splitext(input_data.file_name)[1] or '.pdf'
            unique_filename = f"{uuid4()}{file_extension}"
            file_path = UPLOADS_DIR / unique_filename

            # Save file to disk
            async with aiofiles.open(file_path, 'wb') as f:
                content = await input_data.file.read()
                await f.write(content)

            # Update file_url and file_size
            file_url = f"/uploads/{unique_filename}"
            file_size = len(content)

        # Use display_name if provided, otherwise use file_name
        display_name = input_data.display_name or input_data.file_name

        spec_sheet = SpecSheet(
            manufacturer_id=input_data.manufacturer_id,
            file_name=input_data.file_name,
            display_name=display_name,
            upload_source=input_data.upload_source,
            source_url=input_data.source_url,
            file_url=file_url or "",
            file_size=file_size or 0,
            page_count=input_data.page_count,
            categories=input_data.categories,
            tags=input_data.tags,
            folder_path=input_data.folder_path,
            needs_review=input_data.needs_review,
            published=input_data.published,
            usage_count=0,
            highlight_count=0,
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

        folder_path = input_data.optional_field(input_data.folder_path)
        if folder_path is not None:
            spec_sheet.folder_path = folder_path

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

        Args:
            spec_sheet_id: UUID of the spec sheet to delete

        Returns:
            True if deleted successfully
        """
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

    async def get_spec_sheets_by_manufacturer(
        self, manufacturer_id: UUID, published_only: bool = True
    ) -> list[SpecSheet]:
        """
        Get all spec sheets for a manufacturer.

        Args:
            manufacturer_id: UUID of the manufacturer
            published_only: Filter only published spec sheets

        Returns:
            List of SpecSheet models
        """
        return await self.repository.find_by_manufacturer(
            manufacturer_id, published_only
        )

    async def search_spec_sheets(
        self,
        search_term: str = "",
        manufacturer_id: UUID | None = None,
        categories: list[str] | None = None,
        published_only: bool = True,
        limit: int = 50,
    ) -> list[SpecSheet]:
        """
        Search spec sheets.

        Args:
            search_term: Search term for display_name and file_name
            manufacturer_id: Optional manufacturer filter
            categories: Optional categories filter
            published_only: Filter only published spec sheets
            limit: Maximum number of results

        Returns:
            List of matching SpecSheet models
        """
        return await self.repository.search_spec_sheets(
            search_term, manufacturer_id, categories, published_only, limit
        )

    async def increment_usage(self, spec_sheet_id: UUID) -> None:
        """
        Increment usage count for a spec sheet.

        Args:
            spec_sheet_id: UUID of the spec sheet
        """
        await self.repository.increment_usage_count(spec_sheet_id)

    async def move_folder(
        self,
        manufacturer_id: UUID,
        old_folder_path: str,
        new_folder_path: str,
    ) -> int:
        """
        Move a folder to a new location within the same manufacturer.

        This updates the folder_path of all spec sheets in the folder.

        Args:
            manufacturer_id: UUID of the manufacturer
            old_folder_path: Current path of the folder (e.g., "Folder1/Folder2")
            new_folder_path: New path for the folder (e.g., "Folder3" or "" for root)

        Returns:
            Number of spec sheets updated
        """
        return await self.repository.update_folder_paths(
            manufacturer_id, old_folder_path, new_folder_path
        )
