"""GraphQL queries for SpecSheet Highlights entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.spec_sheets.services.spec_sheet_highlights_service import (
    SpecSheetHighlightsService,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_highlight_response import (
    HighlightVersionResponse,
)


@strawberry.type
class SpecSheetHighlightsQueries:
    """GraphQL queries for SpecSheet Highlights entity."""

    @strawberry.field
    @inject
    async def highlight_version(
        self,
        service: Injected[SpecSheetHighlightsService],
        id: UUID,
    ) -> HighlightVersionResponse | None:
        """
        Get a highlight version by ID.

        Args:
            id: UUID of the version

        Returns:
            HighlightVersionResponse or None if not found
        """
        version = await service.get_highlight_version(id)
        if version:
            return HighlightVersionResponse.from_orm_model(version)
        return None

    @strawberry.field
    @inject
    async def highlight_versions_by_spec_sheet(
        self,
        service: Injected[SpecSheetHighlightsService],
        spec_sheet_id: UUID,
        active_only: bool = False,
    ) -> list[HighlightVersionResponse]:
        """
        Get all highlight versions for a spec sheet.

        Args:
            spec_sheet_id: UUID of the spec sheet
            active_only: If True, only return active versions

        Returns:
            List of HighlightVersionResponse
        """
        versions = await service.get_versions_by_spec_sheet(spec_sheet_id, active_only)
        return [HighlightVersionResponse.from_orm_model(v) for v in versions]
