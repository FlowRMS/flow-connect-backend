from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.files.services.folder_service import FolderService
from app.graphql.v2.files.strawberry.folder_input import (
    CreateFolderInput,
    UpdateFolderInput,
)
from app.graphql.v2.files.strawberry.folder_response import FolderResponse


@strawberry.type
class FolderMutations:
    @strawberry.mutation
    @inject
    async def create_folder(
        self,
        input: CreateFolderInput,
        service: Injected[FolderService],
    ) -> FolderResponse:
        folder = await service.create_folder(
            name=input.name,
            description=input.description,
            parent_id=input.parent_id,
        )
        return FolderResponse.from_orm_model(folder)

    @strawberry.mutation
    @inject
    async def update_folder(
        self,
        input: UpdateFolderInput,
        service: Injected[FolderService],
    ) -> FolderResponse:
        folder = await service.update_folder(
            folder_id=input.folder_id,
            name=input.name,
            description=input.description,
            parent_id=input.parent_id,
        )
        return FolderResponse.from_orm_model(folder)

    @strawberry.mutation
    @inject
    async def archive_folder(
        self,
        folder_id: UUID,
        service: Injected[FolderService],
    ) -> bool:
        return await service.archive_folder(folder_id)

    @strawberry.mutation
    @inject
    async def delete_folder(
        self,
        folder_id: UUID,
        service: Injected[FolderService],
    ) -> bool:
        return await service.delete_folder(folder_id)
