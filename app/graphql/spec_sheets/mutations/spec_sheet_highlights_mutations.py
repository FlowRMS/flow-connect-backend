"""GraphQL mutations for SpecSheet Highlights entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.spec_sheets.services.spec_sheet_highlights_service import (
    SpecSheetHighlightsService,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_highlight_input import (
    CreateHighlightVersionInput,
    UpdateHighlightVersionInput,
    UpdateHighlightRegionsInput,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_highlight_response import (
    HighlightVersionResponse,
)


@strawberry.type
class SpecSheetHighlightsMutations:
    """GraphQL mutations for SpecSheet Highlights entity."""

    @strawberry.mutation
    @inject
    async def create_highlight_version(
        self,
        service: Injected[SpecSheetHighlightsService],
        input: CreateHighlightVersionInput,
    ) -> HighlightVersionResponse:
        """
        Create a new highlight version with regions.

        Args:
            input: Version creation data with regions

        Returns:
            Created HighlightVersionResponse
        """
        version = await service.create_highlight_version(input)
        return HighlightVersionResponse.from_orm_model(version)

    @strawberry.mutation
    @inject
    async def update_highlight_version(
        self,
        service: Injected[SpecSheetHighlightsService],
        id: UUID,
        input: UpdateHighlightVersionInput,
    ) -> HighlightVersionResponse:
        """
        Update a highlight version's metadata.

        Args:
            id: UUID of the version to update
            input: Update data

        Returns:
            Updated HighlightVersionResponse
        """
        version = await service.update_highlight_version(id, input)
        return HighlightVersionResponse.from_orm_model(version)

    @strawberry.mutation
    @inject
    async def update_highlight_regions(
        self,
        service: Injected[SpecSheetHighlightsService],
        input: UpdateHighlightRegionsInput,
    ) -> HighlightVersionResponse:
        """
        Replace all regions in a version with new ones.

        Args:
            input: Version ID and new regions data

        Returns:
            Updated HighlightVersionResponse
        """
        version = await service.update_version_regions(input)
        return HighlightVersionResponse.from_orm_model(version)

    @strawberry.mutation
    @inject
    async def delete_highlight_version(
        self,
        service: Injected[SpecSheetHighlightsService],
        id: UUID,
    ) -> bool:
        """
        Delete a highlight version and all its regions.

        Args:
            id: UUID of the version to delete

        Returns:
            True if deleted successfully
        """
        return await service.delete_highlight_version(id)
