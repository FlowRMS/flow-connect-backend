from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.files import File, FileType
from strawberry.file_uploads import Upload

from app.graphql.v2.files.repositories.file_repository import FileRepository
from app.graphql.v2.files.services.file_upload_service import FileUploadService

FILE_TYPE_EXTENSIONS: dict[str, FileType] = {
    ".pdf": FileType.PDF,
    ".doc": FileType.DOCUMENT,
    ".docx": FileType.DOCUMENT,
    ".txt": FileType.DOCUMENT,
    ".rtf": FileType.DOCUMENT,
    ".odt": FileType.DOCUMENT,
    ".jpg": FileType.IMAGE,
    ".jpeg": FileType.IMAGE,
    ".png": FileType.IMAGE,
    ".gif": FileType.IMAGE,
    ".bmp": FileType.IMAGE,
    ".webp": FileType.IMAGE,
    ".svg": FileType.IMAGE,
    ".xls": FileType.SPREADSHEET,
    ".xlsx": FileType.SPREADSHEET,
    ".csv": FileType.SPREADSHEET,
    ".ods": FileType.SPREADSHEET,
    ".ppt": FileType.PRESENTATION,
    ".pptx": FileType.PRESENTATION,
    ".odp": FileType.PRESENTATION,
    ".mp4": FileType.VIDEO,
    ".avi": FileType.VIDEO,
    ".mov": FileType.VIDEO,
    ".wmv": FileType.VIDEO,
    ".webm": FileType.VIDEO,
    ".mp3": FileType.AUDIO,
    ".wav": FileType.AUDIO,
    ".ogg": FileType.AUDIO,
    ".flac": FileType.AUDIO,
    ".zip": FileType.ARCHIVE,
    ".rar": FileType.ARCHIVE,
    ".7z": FileType.ARCHIVE,
    ".tar": FileType.ARCHIVE,
    ".gz": FileType.ARCHIVE,
}


def detect_file_type(file_name: str) -> FileType:
    extension = "." + file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    return FILE_TYPE_EXTENSIONS.get(extension, FileType.OTHER)


class FileService:
    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        repository: FileRepository,
        upload_service: FileUploadService,
        auth_info: AuthInfo,
    ) -> None:
        self.repository = repository
        self.upload_service = upload_service
        self.auth_info = auth_info

    async def get_by_id(self, file_id: UUID) -> File | None:
        return await self.repository.get_by_id(file_id)

    async def search_files(self, search_term: str, limit: int = 20) -> list[File]:
        return await self.repository.search_by_name(search_term, limit)

    async def find_by_folder(self, folder_id: UUID) -> list[File]:
        return await self.repository.find_by_folder(folder_id)

    async def upload_file(
        self,
        file: Upload,
        file_name: str,
        folder_id: UUID | None = None,
        folder_path: str | None = None,
    ) -> File:
        content = await file.read()
        upload_result = await self.upload_service.upload_file(
            file_content=content,
            file_name=file_name,
            folder_path=folder_path,
        )
        file_type = detect_file_type(file_name)
        new_file = File(
            file_name=file_name,
            file_path=upload_result.file_path,
            file_size=upload_result.file_size,
            file_type=file_type,
            file_sha=upload_result.file_sha,
            folder_id=folder_id,
        )
        return await self.repository.create(new_file)

    async def upload_files(
        self,
        files: list[tuple[Upload, str]],
        folder_id: UUID | None = None,
        folder_path: str | None = None,
    ) -> list[File]:
        results: list[File] = []
        for file, file_name in files:
            result = await self.upload_file(file, file_name, folder_id, folder_path)
            results.append(result)
        return results

    async def archive_file(self, file_id: UUID) -> bool:
        return await self.repository.archive(file_id)

    async def delete_file(self, file_id: UUID) -> bool:
        file = await self.repository.get_by_id(file_id)
        if not file:
            return False
        s3_key = self.upload_service.extract_s3_key_from_path(file.file_path)
        if s3_key:
            await self.upload_service.delete_file(s3_key)
        return await self.repository.delete(file_id)

    async def get_presigned_url(self, file_id: UUID) -> str | None:
        file = await self.repository.get_by_id(file_id)
        if not file:
            return None
        s3_key = self.upload_service.extract_s3_key_from_path(file.file_path)
        return await self.upload_service.get_presigned_url(s3_key)
