from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.inject import inject
from app.graphql.v2.files.services.file_service import FileService
from app.graphql.v2.files.strawberry.file_response import FileResponse


@strawberry.type
class FileQueries:
    @strawberry.field
    @inject
    async def file(
        self,
        file_id: UUID,
        service: Injected[FileService],
    ) -> FileResponse | None:
        return FileResponse.from_orm_model_optional(await service.get_by_id(file_id))

    @strawberry.field
    @inject
    async def search_files(
        self,
        search_term: str,
        service: Injected[FileService],
        limit: int = 20,
    ) -> list[FileResponse]:
        files = await service.search_files(search_term, limit)
        return FileResponse.from_orm_model_list(files)

    @strawberry.field
    @inject
    async def files_by_folder(
        self,
        folder_id: UUID,
        service: Injected[FileService],
    ) -> list[FileResponse]:
        files = await service.find_by_folder(folder_id)
        return FileResponse.from_orm_model_list(files)

    @strawberry.field
    @inject
    async def file_presigned_url(
        self,
        file_id: UUID,
        service: Injected[FileService],
    ) -> str | None:
        return await service.get_presigned_url(file_id)

    @strawberry.field
    @inject
    async def files_by_linked_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
        service: Injected[FileService],
    ) -> list[FileResponse]:
        files = await service.find_by_linked_entity(entity_type, entity_id)
        return FileResponse.from_orm_model_list(files)
