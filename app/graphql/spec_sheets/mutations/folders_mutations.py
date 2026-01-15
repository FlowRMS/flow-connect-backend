"""GraphQL mutations for Folder entity."""

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.spec_sheets.services.folders_service import FoldersService
from app.graphql.spec_sheets.strawberry.folder_input import (
    CreateFolderInput,
    DeleteFolderInput,
    RenameFolderInput,
)
from app.graphql.spec_sheets.strawberry.folder_response import (
    RenameSpecSheetFolderResult,
    SpecSheetFolderResponse,
)


@strawberry.type
class FoldersMutations:
    """GraphQL mutations for Folder entity."""

    @strawberry.mutation
    @inject
    async def create_folder(
        self,
        service: Injected[FoldersService],
        input: CreateFolderInput,
    ) -> SpecSheetFolderResponse:
        """
        Create a new folder.

        Args:
            input: Folder creation data with factory_id, parent_path, folder_name

        Returns:
            Created SpecSheetFolderResponse
        """
        folder = await service.create_subfolder(
            input.factory_id,
            input.parent_path,
            input.folder_name,
        )
        return SpecSheetFolderResponse.from_orm_model(folder)

    @strawberry.mutation
    @inject
    async def rename_folder(
        self,
        service: Injected[FoldersService],
        input: RenameFolderInput,
    ) -> RenameSpecSheetFolderResult:
        """
        Rename a folder and update all spec sheets in it.

        Args:
            input: Rename data with factory_id, folder_path, new_name

        Returns:
            RenameSpecSheetFolderResult with updated folder and count of updated spec sheets
        """
        folder, spec_count = await service.rename_folder(
            input.factory_id,
            input.folder_path,
            input.new_name,
        )
        return RenameSpecSheetFolderResult(
            folder=SpecSheetFolderResponse.from_orm_model(folder),
            spec_sheets_updated=spec_count,
        )

    @strawberry.mutation
    @inject
    async def delete_folder(
        self,
        service: Injected[FoldersService],
        input: DeleteFolderInput,
    ) -> bool:
        """
        Delete a folder only if it has no spec sheets.

        Args:
            input: Delete data with factory_id, folder_path

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If folder has spec sheets and cannot be deleted
        """
        return await service.delete_folder(
            input.factory_id,
            input.folder_path,
        )
