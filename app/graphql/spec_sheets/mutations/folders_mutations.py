import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.spec_sheets.services.folders_service import FoldersService
from app.graphql.spec_sheets.strawberry.create_spec_sheet_folder_input import (
    CreateSpecSheetFolderInput,
)
from app.graphql.spec_sheets.strawberry.delete_spec_sheet_folder_input import (
    DeleteSpecSheetFolderInput,
)
from app.graphql.spec_sheets.strawberry.folder_response import SpecSheetFolderResponse
from app.graphql.spec_sheets.strawberry.move_spec_sheet_folder_input import (
    MoveSpecSheetFolderInput,
)
from app.graphql.spec_sheets.strawberry.rename_spec_sheet_folder_input import (
    RenameSpecSheetFolderInput,
)


@strawberry.type
class FoldersMutations:
    """GraphQL mutations for Folder entity using pyfiles.folders."""

    @strawberry.mutation
    @inject
    async def create_spec_sheet_folder(
        self,
        service: Injected[FoldersService],
        input: CreateSpecSheetFolderInput,
    ) -> SpecSheetFolderResponse:
        """
        Create a new folder for spec sheets.

        Args:
            input: Folder creation data with factory_id, parent_folder_id, folder_name

        Returns:
            Created SpecSheetFolderResponse
        """
        folder = await service.create_folder(
            factory_id=input.factory_id,
            name=input.folder_name,
            parent_folder_id=input.parent_folder_id,
        )
        return SpecSheetFolderResponse.from_folder(folder, input.factory_id)

    @strawberry.mutation
    @inject
    async def rename_spec_sheet_folder(
        self,
        service: Injected[FoldersService],
        input: RenameSpecSheetFolderInput,
    ) -> SpecSheetFolderResponse:
        """
        Rename a spec sheet folder.

        Args:
            input: Rename data with factory_id, folder_id, new_name

        Returns:
            Updated SpecSheetFolderResponse
        """
        folder = await service.rename_folder(
            factory_id=input.factory_id,
            folder_id=input.folder_id,
            new_name=input.new_name,
        )
        return SpecSheetFolderResponse.from_folder(folder, input.factory_id)

    @strawberry.mutation
    @inject
    async def delete_spec_sheet_folder(
        self,
        service: Injected[FoldersService],
        input: DeleteSpecSheetFolderInput,
    ) -> bool:
        """
        Delete a spec sheet folder only if it has no spec sheets.

        Args:
            input: Delete data with factory_id, folder_id

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If folder has spec sheets and cannot be deleted
        """
        return await service.delete_folder(
            factory_id=input.factory_id,
            folder_id=input.folder_id,
        )

    @strawberry.mutation
    @inject
    async def move_spec_sheet_folder(
        self,
        service: Injected[FoldersService],
        input: MoveSpecSheetFolderInput,
    ) -> SpecSheetFolderResponse:
        """
        Move a folder to a new parent.

        Args:
            input: Move data with factory_id, folder_id, new_parent_id

        Returns:
            Updated SpecSheetFolderResponse
        """
        folder = await service.move_folder(
            factory_id=input.factory_id,
            folder_id=input.folder_id,
            new_parent_id=input.new_parent_id,
        )
        return SpecSheetFolderResponse.from_folder(folder, input.factory_id)
