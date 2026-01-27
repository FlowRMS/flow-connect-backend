"""GraphQL queries for spec sheet folders using pyfiles.folders."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.spec_sheets.services.folders_service import FoldersService
from app.graphql.spec_sheets.strawberry.folder_response import (
    SpecSheetFolderResponse,
)


@strawberry.type
class FoldersQueries:
    """GraphQL queries for spec sheet folders using pyfiles.folders."""

    @strawberry.field
    @inject
    async def folders_by_factory(
        self,
        service: Injected[FoldersService],
        factory_id: UUID,
    ) -> list[SpecSheetFolderResponse]:
        """
        Get all folders for a factory with recursive spec sheet counts.

        Returns folders from pyfiles.folders that are mapped to this factory.
        Counts include spec sheets in subfolders.

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
        return [
            SpecSheetFolderResponse.from_folder(folder, factory_id, 0)
            for folder in folders
        ]

    @strawberry.field
    @inject
    async def folder_children(
        self,
        service: Injected[FoldersService],
        factory_id: UUID,
        folder_id: UUID,
    ) -> list[SpecSheetFolderResponse]:
        """
        Get child folders of a parent folder.

        Args:
            factory_id: UUID of the factory
            folder_id: UUID of the parent folder

        Returns:
            List of child SpecSheetFolderResponse
        """
        children = await service.get_children(factory_id, folder_id)
        return [
            SpecSheetFolderResponse.from_folder(child, factory_id, 0)
            for child in children
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
        Get a specific folder by ID.

        Args:
            factory_id: UUID of the factory
            folder_id: UUID of the folder

        Returns:
            SpecSheetFolderResponse or None if not found
        """
        folder = await service.get_folder(folder_id)
        if folder:
            count = await service.get_spec_sheet_count(factory_id, folder_id)
            return SpecSheetFolderResponse.from_folder(folder, factory_id, count)
        return None
