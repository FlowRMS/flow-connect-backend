from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.files.services.file_service import FileService
from app.graphql.v2.files.strawberry.file_response import FileLiteResponse, FileResponse
from app.graphql.v2.files.strawberry.file_upload_input import FileUploadInput
from app.graphql.v2.files.strawberry.multi_file_upload_input import MultiFileUploadInput


@strawberry.type
class FileMutations:
    @strawberry.mutation
    @inject
    async def upload_file(
        self,
        input: FileUploadInput,
        service: Injected[FileService],
    ) -> FileResponse:
        file = await service.upload_file(
            file_upload=input.file,
            file_name=input.file_name,
            folder_id=input.folder_id,
            folder_path=input.folder_path,
            file_entity_type=input.file_entity_type,
        )
        return FileResponse.from_orm_model(file)

    @strawberry.mutation
    @inject
    async def upload_files(
        self,
        input: MultiFileUploadInput,
        service: Injected[FileService],
    ) -> list[FileLiteResponse]:
        if len(input.files) != len(input.file_names):
            raise ValueError("Number of files must match number of file names")
        files_with_names = list(zip(input.files, input.file_names, strict=True))
        files = await service.upload_files(
            files=files_with_names,
            folder_id=input.folder_id,
            folder_path=input.folder_path,
        )
        return FileLiteResponse.from_orm_model_list(files)

    @strawberry.mutation
    @inject
    async def archive_file(
        self,
        file_id: UUID,
        service: Injected[FileService],
    ) -> bool:
        return await service.archive_file(file_id)

    @strawberry.mutation
    @inject
    async def delete_file(
        self,
        file_id: UUID,
        service: Injected[FileService],
    ) -> bool:
        return await service.delete_file(file_id)
