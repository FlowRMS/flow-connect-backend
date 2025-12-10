"""GraphQL queries for SpecSheets entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.spec_sheets.services.spec_sheets_service import SpecSheetsService
from app.graphql.spec_sheets.strawberry.spec_sheet_response import SpecSheetResponse


@strawberry.type
class SpecSheetsQueries:
    """GraphQL queries for SpecSheets entity."""

    @strawberry.field
    @inject
    async def spec_sheet(
        self,
        service: Injected[SpecSheetsService],
        id: UUID,
    ) -> SpecSheetResponse | None:
        """
        Get a spec sheet by ID.

        Args:
            id: UUID of the spec sheet

        Returns:
            SpecSheetResponse or None if not found
        """
        spec_sheet = await service.get_spec_sheet(id)
        if not spec_sheet:
            return None
        return SpecSheetResponse.from_orm_model(spec_sheet)

    @strawberry.field
    @inject
    async def spec_sheets_by_manufacturer(
        self,
        service: Injected[SpecSheetsService],
        manufacturer_id: UUID,
        published_only: bool = True,
    ) -> list[SpecSheetResponse]:
        """
        Get all spec sheets for a manufacturer.

        Args:
            manufacturer_id: UUID of the manufacturer
            published_only: Filter only published spec sheets

        Returns:
            List of SpecSheetResponse
        """
        spec_sheets = await service.get_spec_sheets_by_manufacturer(
            manufacturer_id, published_only
        )
        return SpecSheetResponse.from_orm_model_list(spec_sheets)

    @strawberry.field
    @inject
    async def spec_sheet_search(
        self,
        service: Injected[SpecSheetsService],
        search_term: str = "",
        manufacturer_id: UUID | None = None,
        categories: list[str] | None = None,
        published_only: bool = True,
        limit: int = 50,
    ) -> list[SpecSheetResponse]:
        """
        Search spec sheets.

        Args:
            search_term: Search term for display_name and file_name
            manufacturer_id: Optional manufacturer filter
            categories: Optional categories filter
            published_only: Filter only published spec sheets
            limit: Maximum number of results

        Returns:
            List of matching SpecSheetResponse
        """
        spec_sheets = await service.search_spec_sheets(
            search_term, manufacturer_id, categories, published_only, limit
        )
        return SpecSheetResponse.from_orm_model_list(spec_sheets)
