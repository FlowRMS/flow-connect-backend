"""GraphQL mutations for SpecSheets entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.spec_sheets.services.spec_sheets_service import SpecSheetsService
from app.graphql.spec_sheets.strawberry.spec_sheet_input import (
    CreateSpecSheetInput,
    MoveFolderInput,
    UpdateSpecSheetInput,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_response import SpecSheetResponse


@strawberry.type
class SpecSheetsMutations:
    """GraphQL mutations for SpecSheets entity."""

    @strawberry.mutation
    @inject
    async def create_spec_sheet(
        self,
        service: Injected[SpecSheetsService],
        input: CreateSpecSheetInput,
    ) -> SpecSheetResponse:
        """
        Create a new spec sheet.

        Args:
            input: Spec sheet creation data

        Returns:
            Created SpecSheetResponse
        """
        spec_sheet = await service.create_spec_sheet(input)
        return SpecSheetResponse.from_orm_model(spec_sheet)

    @strawberry.mutation
    @inject
    async def update_spec_sheet(
        self,
        service: Injected[SpecSheetsService],
        id: UUID,
        input: UpdateSpecSheetInput,
    ) -> SpecSheetResponse:
        """
        Update an existing spec sheet.

        Args:
            id: UUID of the spec sheet to update
            input: Update data

        Returns:
            Updated SpecSheetResponse
        """
        spec_sheet = await service.update_spec_sheet(id, input)
        return SpecSheetResponse.from_orm_model(spec_sheet)

    @strawberry.mutation
    @inject
    async def delete_spec_sheet(
        self,
        service: Injected[SpecSheetsService],
        id: UUID,
    ) -> bool:
        """
        Delete a spec sheet.

        Args:
            id: UUID of the spec sheet to delete

        Returns:
            True if deleted successfully
        """
        return await service.delete_spec_sheet(id)

    @strawberry.mutation
    @inject
    async def increment_spec_sheet_usage(
        self,
        service: Injected[SpecSheetsService],
        id: UUID,
    ) -> bool:
        """
        Increment usage count for a spec sheet.

        Args:
            id: UUID of the spec sheet

        Returns:
            True if incremented successfully
        """
        await service.increment_usage(id)
        return True

    @strawberry.mutation
    @inject
    async def move_folder(
        self,
        service: Injected[SpecSheetsService],
        input: MoveFolderInput,
    ) -> int:
        """
        Move a folder to a new location within the same factory.

        Updates the folder_path of all spec sheets in the folder.

        Args:
            input: Move folder data with factory_id, old_folder_path, new_folder_path

        Returns:
            Number of spec sheets updated
        """
        return await service.move_folder(
            input.factory_id,
            input.old_folder_path,
            input.new_folder_path,
        )
