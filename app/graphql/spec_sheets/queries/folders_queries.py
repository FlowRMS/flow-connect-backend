"""GraphQL queries for Folder entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.spec_sheets.services.folders_service import FoldersService
from app.graphql.spec_sheets.strawberry.folder_response import (
    FolderPathWithCount,
    SpecSheetFolderResponse,
)


@strawberry.type
class FoldersQueries:
    """GraphQL queries for Folder entity."""

    @strawberry.field
    @inject
    async def folders_by_factory(
        self,
        service: Injected[FoldersService],
        factory_id: UUID,
    ) -> list[SpecSheetFolderResponse]:
        """
        Get all folders for a factory with spec sheet counts.

        Returns folders derived from spec sheets (including virtual folders
        that don't exist in the folders table). Counts are recursive.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of SpecSheetFolderResponse with spec_sheet_count
        """
        paths_with_counts = await service.get_folder_paths_with_counts(factory_id)
        return [
            SpecSheetFolderResponse.from_path(factory_id, path, count)
            for path, count in paths_with_counts
        ]

    @strawberry.field
    @inject
    async def folder_paths_by_factory(
        self,
        service: Injected[FoldersService],
        factory_id: UUID,
    ) -> list[FolderPathWithCount]:
        """
        Get all folder paths with spec sheet counts for a factory.

        This returns folder paths derived from spec sheets, including virtual
        folders that don't exist in the folders table. Counts are recursive
        (parent folders include counts from subfolders).

        Args:
            factory_id: UUID of the factory

        Returns:
            List of FolderPathWithCount
        """
        paths_with_counts = await service.get_folder_paths_with_counts(factory_id)
        return [
            FolderPathWithCount(folder_path=path, spec_sheet_count=count)
            for path, count in paths_with_counts
        ]
