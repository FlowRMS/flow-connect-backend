from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.files.services.folder_service import FolderService
from app.graphql.v2.files.strawberry.folder_response import (
    FolderResponse,
    FolderWithChildrenResponse,
)


@strawberry.type
class FolderQueries:
    @strawberry.field
    @inject
    async def folder(
        self,
        folder_id: UUID,
        service: Injected[FolderService],
    ) -> FolderResponse | None:
        folder = await service.get_by_id(folder_id)
        return FolderResponse.from_orm_model_optional(folder)

    @strawberry.field
    @inject
    async def folder_with_contents(
        self,
        folder_id: UUID,
        service: Injected[FolderService],
    ) -> FolderWithChildrenResponse | None:
        folder = await service.get_with_relations(folder_id)
        return FolderWithChildrenResponse.from_orm_model_optional(folder)

    @strawberry.field
    @inject
    async def search_folders(
        self,
        search_term: str,
        service: Injected[FolderService],
        limit: int = 20,
    ) -> list[FolderResponse]:
        folders = await service.search_folders(search_term, limit)
        return FolderResponse.from_orm_model_list(folders)

    @strawberry.field
    @inject
    async def folders_by_parent(
        self,
        service: Injected[FolderService],
        parent_id: UUID | None = None,
    ) -> list[FolderResponse]:
        folders = await service.find_by_parent(parent_id)
        return FolderResponse.from_orm_model_list(folders)

    @strawberry.field
    @inject
    async def root_folders(
        self,
        service: Injected[FolderService],
    ) -> list[FolderResponse]:
        folders = await service.get_root_folders()
        return FolderResponse.from_orm_model_list(folders)
