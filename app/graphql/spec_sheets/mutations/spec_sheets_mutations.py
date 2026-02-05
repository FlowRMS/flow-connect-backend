from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.spec_sheets.services.spec_sheets_service import SpecSheetsService
from app.graphql.spec_sheets.strawberry.move_spec_sheet_to_folder_input import (
    MoveSpecSheetToFolderInput,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_input import (
    CreateSpecSheetInput,
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
            input: Spec sheet creation data including optional folder_id

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

        Note: To move a spec sheet to a different folder, use moveSpecSheetToFolder.

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
    async def move_spec_sheet_to_folder(
        self,
        service: Injected[SpecSheetsService],
        input: MoveSpecSheetToFolderInput,
    ) -> SpecSheetResponse | None:
        """
        Move a spec sheet to a different folder (drag and drop).

        Updates the File.folder_id to move the spec sheet.

        Args:
            input: Move data with spec_sheet_id, folder_id

        Returns:
            Updated SpecSheetResponse or None if not found
        """
        spec_sheet = await service.move_spec_sheet_to_folder(
            spec_sheet_id=input.spec_sheet_id,
            folder_id=input.folder_id,
        )
        if spec_sheet:
            return SpecSheetResponse.from_orm_model(spec_sheet)
        return None
