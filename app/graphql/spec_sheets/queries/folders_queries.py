"""GraphQL queries for Folder entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.spec_sheets.services.folders_service import FoldersService
from app.graphql.spec_sheets.strawberry.folder_response import SpecSheetFolderResponse


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
        Get all folders for a factory.

        Args:
            factory_id: UUID of the factory

        Returns:
            List of SpecSheetFolderResponse
        """
        folders = await service.get_folders_by_factory(factory_id)
        return [SpecSheetFolderResponse.from_orm_model(f) for f in folders]
