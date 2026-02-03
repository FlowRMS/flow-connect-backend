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
    async def spec_sheets_by_factory(
        self,
        service: Injected[SpecSheetsService],
        factory_id: UUID,
        published_only: bool = True,
    ) -> list[SpecSheetResponse]:
        """
        Get all spec sheets for a factory.

        Args:
            factory_id: UUID of the factory
            published_only: Filter only published spec sheets

        Returns:
            List of SpecSheetResponse
        """
        spec_sheets = await service.get_spec_sheets_by_factory(
            factory_id, published_only
        )
        return SpecSheetResponse.from_orm_model_list(spec_sheets)

    @strawberry.field
    @inject
    async def spec_sheet_search(
        self,
        service: Injected[SpecSheetsService],
        search_term: str = "",
        factory_id: UUID | None = None,
        categories: list[str] | None = None,
        published_only: bool = True,
        limit: int = 50,
    ) -> list[SpecSheetResponse]:
        """
        Search spec sheets.

        Args:
            search_term: Search term for display_name and file_name
            factory_id: Optional factory filter
            categories: Optional categories filter
            published_only: Filter only published spec sheets
            limit: Maximum number of results

        Returns:
            List of matching SpecSheetResponse
        """
        spec_sheets = await service.search_spec_sheets(
            search_term, factory_id, categories, published_only, limit
        )
        return SpecSheetResponse.from_orm_model_list(spec_sheets)

    @strawberry.field
    @inject
    async def spec_sheets_by_folder(
        self,
        service: Injected[SpecSheetsService],
        factory_id: UUID,
        folder_id: UUID | None = None,
        published_only: bool = True,
    ) -> list[SpecSheetResponse]:
        """
        Get all spec sheets in a specific folder.

        Args:
            factory_id: UUID of the factory
            folder_id: UUID of the folder (None for root/unassigned)
            published_only: Filter only published spec sheets

        Returns:
            List of SpecSheetResponse in the folder
        """
        spec_sheets = await service.get_spec_sheets_by_folder(
            factory_id, folder_id, published_only
        )
        return SpecSheetResponse.from_orm_model_list(spec_sheets)
