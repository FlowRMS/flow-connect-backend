from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.spec_sheets.services.folders_service import FoldersService
from app.graphql.spec_sheets.strawberry.folder_response import SpecSheetFolderResponse


@strawberry.type
class FoldersQueries:
    """GraphQL queries for Folder entity using pyfiles.folders."""

    @strawberry.field
    @inject
    async def folders_by_factory(
        self,
        service: Injected[FoldersService],
        factory_id: UUID,
    ) -> list[SpecSheetFolderResponse]:
        """
        Get all pyfiles.folders for a factory with spec sheet counts.

        Returns folders from pyfiles.folders table with recursive counts.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of SpecSheetFolderResponse with spec_sheet_count
        """
        folders_with_counts = await service.get_folders_by_factory_with_counts(
            factory_id
        )
        return [
            SpecSheetFolderResponse.from_folder(folder, factory_id, count)
            for folder, count in folders_with_counts
        ]

    @strawberry.field
    @inject
    async def folder_by_id(
        self,
        service: Injected[FoldersService],
        factory_id: UUID,
        folder_id: UUID,
    ) -> SpecSheetFolderResponse | None:
        """
        Get a single folder by ID.

        Args:
            factory_id: UUID of the factory
            folder_id: UUID of the folder

        Returns:
            SpecSheetFolderResponse if found, None otherwise
        """
        folder = await service.get_folder(folder_id)
        if not folder:
            return None
        count = await service.get_spec_sheet_count(factory_id, folder_id)
        return SpecSheetFolderResponse.from_folder(folder, factory_id, count)

    @strawberry.field
    @inject
    async def root_folders_by_factory(
        self,
        service: Injected[FoldersService],
        factory_id: UUID,
    ) -> list[SpecSheetFolderResponse]:
        """
        Get root folders (no parent) for a factory.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of root SpecSheetFolderResponse
        """
        folders = await service.get_root_folders(factory_id)
        result = []
        for folder in folders:
            count = await service.get_spec_sheet_count(factory_id, folder.id)
            result.append(
                SpecSheetFolderResponse.from_folder(folder, factory_id, count)
            )
        return result

    @strawberry.field
    @inject
    async def child_folders(
        self,
        service: Injected[FoldersService],
        factory_id: UUID,
        parent_id: UUID,
    ) -> list[SpecSheetFolderResponse]:
        """
        Get child folders of a parent folder.

        Args:
            factory_id: UUID of the factory
            parent_id: UUID of the parent folder

        Returns:
            List of child SpecSheetFolderResponse
        """
        folders = await service.get_children(factory_id, parent_id)
        result = []
        for folder in folders:
            count = await service.get_spec_sheet_count(factory_id, folder.id)
            result.append(
                SpecSheetFolderResponse.from_folder(folder, factory_id, count)
            )
        return result
