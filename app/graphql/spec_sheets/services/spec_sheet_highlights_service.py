"""Service layer for SpecSheet Highlights business logic."""

from uuid import UUID

from commons.db.v6.crm.spec_sheets.spec_sheet_highlight_model import (
    SpecSheetHighlightVersion,
)

from app.graphql.spec_sheets.repositories.spec_sheet_highlights_repository import (
    SpecSheetHighlightsRepository,
)
from app.graphql.spec_sheets.repositories.spec_sheets_repository import (
    SpecSheetsRepository,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_highlight_input import (
    CreateHighlightVersionInput,
    UpdateHighlightRegionsInput,
    UpdateHighlightVersionInput,
)


class SpecSheetHighlightsService:
    """Service for SpecSheet Highlights business logic."""

    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        repository: SpecSheetHighlightsRepository,
        spec_sheets_repository: SpecSheetsRepository,
    ) -> None:
        """
        Initialize the Highlights service.

        Args:
            repository: Highlights repository instance
            spec_sheets_repository: SpecSheets repository for updating highlight count
        """
        self.repository = repository
        self.spec_sheets_repository = spec_sheets_repository

    async def create_highlight_version(
        self, input_data: CreateHighlightVersionInput
    ) -> SpecSheetHighlightVersion:
        """
        Create a new highlight version with regions.

        Args:
            input_data: Version creation data with regions

        Returns:
            Created SpecSheetHighlightVersion with regions
        """
        # Convert input regions to dictionaries
        regions_data = [
            {
                "page_number": r.page_number,
                "x": r.x,
                "y": r.y,
                "width": r.width,
                "height": r.height,
                "shape_type": r.shape_type,
                "color": r.color,
                "annotation": r.annotation,
                "tags": r.tags,
            }
            for r in input_data.regions
        ]

        # Create version with regions
        version = await self.repository.create_version_with_regions(
            spec_sheet_id=input_data.spec_sheet_id,
            name=input_data.name,
            description=input_data.description,
            regions_data=regions_data,
        )

        # Update highlight count on spec sheet
        await self._update_highlight_count(input_data.spec_sheet_id)

        return version

    async def get_highlight_version(
        self, version_id: UUID
    ) -> SpecSheetHighlightVersion | None:
        """
        Get a highlight version by ID with its regions.

        Args:
            version_id: UUID of the version

        Returns:
            SpecSheetHighlightVersion or None
        """
        return await self.repository.get_version_with_regions(version_id)

    async def get_versions_by_spec_sheet(
        self, spec_sheet_id: UUID, active_only: bool = False
    ) -> list[SpecSheetHighlightVersion]:
        """
        Get all highlight versions for a spec sheet.

        Args:
            spec_sheet_id: UUID of the spec sheet
            active_only: If True, only return active versions

        Returns:
            List of SpecSheetHighlightVersion with regions
        """
        return await self.repository.find_by_spec_sheet(spec_sheet_id, active_only)

    async def update_highlight_version(
        self, version_id: UUID, input_data: UpdateHighlightVersionInput
    ) -> SpecSheetHighlightVersion:
        """
        Update a highlight version's metadata.

        Args:
            version_id: UUID of the version
            input_data: Update data

        Returns:
            Updated SpecSheetHighlightVersion

        Raises:
            ValueError: If version not found
        """
        version = await self.repository.get_by_id(version_id)
        if not version:
            raise ValueError(f"Highlight version with id {version_id} not found")

        # Update fields if provided
        if input_data.name is not None:
            version.name = input_data.name
        if input_data.description is not None:
            version.description = input_data.description
        if input_data.is_active is not None:
            version.is_active = input_data.is_active

        _ = await self.repository.update(version)
        result = await self.repository.get_version_with_regions(version_id)
        assert result is not None  # Version was just updated
        return result

    async def update_version_regions(
        self, input_data: UpdateHighlightRegionsInput
    ) -> SpecSheetHighlightVersion:
        """
        Replace all regions in a version with new ones.

        Args:
            input_data: Version ID and new regions

        Returns:
            Updated SpecSheetHighlightVersion with new regions

        Raises:
            ValueError: If version not found
        """
        # Convert input regions to dictionaries
        regions_data = [
            {
                "page_number": r.page_number,
                "x": r.x,
                "y": r.y,
                "width": r.width,
                "height": r.height,
                "shape_type": r.shape_type,
                "color": r.color,
                "annotation": r.annotation,
                "tags": r.tags,
            }
            for r in input_data.regions
        ]

        version = await self.repository.update_version_regions(
            input_data.version_id, regions_data
        )

        if not version:
            raise ValueError(
                f"Highlight version with id {input_data.version_id} not found"
            )

        # Update highlight count on spec sheet
        await self._update_highlight_count(version.spec_sheet_id)

        return version

    async def delete_highlight_version(self, version_id: UUID) -> bool:
        """
        Delete a highlight version and all its regions.

        Args:
            version_id: UUID of the version to delete

        Returns:
            True if deleted successfully
        """
        # Get spec_sheet_id before deletion
        version = await self.repository.get_by_id(version_id)
        if not version:
            return False

        spec_sheet_id = version.spec_sheet_id
        result = await self.repository.delete_version(version_id)

        if result:
            # Update highlight count on spec sheet
            await self._update_highlight_count(spec_sheet_id)

        return result

    async def _update_highlight_count(self, spec_sheet_id: UUID) -> None:
        """
        Update the highlight_count on a spec sheet based on total regions.

        Args:
            spec_sheet_id: UUID of the spec sheet
        """
        count = await self.repository.count_regions_by_spec_sheet(spec_sheet_id)
        spec_sheet = await self.spec_sheets_repository.get_by_id(spec_sheet_id)
        if spec_sheet:
            spec_sheet.highlight_count = count
            _ = await self.spec_sheets_repository.update(spec_sheet)
