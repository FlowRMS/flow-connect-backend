from asyncio import gather
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.enums import DocumentEntityType
from commons.db.v6.files import File, FileType
from commons.utils.pdf_extractor.pdf import PDFExtractor
from loguru import logger
from sqlalchemy.orm import joinedload, lazyload
from strawberry.file_uploads import Upload

from app.graphql.v2.files.repositories.file_repository import FileRepository
from app.graphql.v2.files.repositories.vector_repository import VectorRepository
from app.graphql.v2.files.services.file_upload_service import FileUploadService

MAX_PDF_PAGES = 50

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
    def __init__(
        self,
        repository: FileRepository,
        upload_service: FileUploadService,
        auth_info: AuthInfo,
        vector_repository: VectorRepository,
        pdf_extractor: PDFExtractor,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.upload_service = upload_service
        self.auth_info = auth_info
        self.vector_repository = vector_repository
        self.pdf_extractor = pdf_extractor

    async def get_by_id(self, file_id: UUID) -> File:
        file = await self.repository.get_by_id(
            file_id,
            options=[
                joinedload(File.created_by),
                lazyload("*"),
            ],
        )
        if not file:
            raise ValueError(f"File with id {file_id} not found")

        return file

    async def search_files(self, search_term: str, limit: int = 20) -> list[File]:
        return await self.repository.search_by_name(search_term, limit)

    async def find_by_folder(self, folder_id: UUID) -> list[File]:
        return await self.repository.find_by_folder(folder_id)

    async def upload_file(
        self,
        file_upload: Upload,
        file_name: str,
        file_entity_type: DocumentEntityType | None = None,
        folder_id: UUID | None = None,
        folder_path: str | None = None,
    ) -> File:
        content: bytes = await file_upload.read()
        upload_result = await self.upload_service.upload_file(
            file_content=content,
            file_name=file_name,
            folder_path=folder_path,
        )
        file_type = detect_file_type(file_name)
        new_file = File(
            file_name=file_name,
            file_path=upload_result.file_path,  # folder_path without filename
            file_size=upload_result.file_size,
            file_type=file_type,
            file_sha=upload_result.file_sha,
            folder_id=folder_id,
            file_entity_type=file_entity_type,
        )
        file = await self.repository.create(new_file)
        await self.vectorize_file(content, file)
        return await self.get_by_id(file.id)

    async def upload_files(
        self,
        files: list[tuple[Upload, str]],
        folder_id: UUID | None = None,
        folder_path: str | None = None,
        file_entity_type: DocumentEntityType | None = None,
    ) -> list[File]:
        results: list[File] = []
        for file, file_name in files:
            result = await self.upload_file(
                file,
                file_name,
                file_entity_type=file_entity_type,
                folder_id=folder_id,
                folder_path=folder_path,
            )
            results.append(result)
        return results

    async def vectorize_file(self, file_bytes: bytes, file: File) -> None:
        if file.file_type == FileType.PDF:
            page_contents: list[str] = self.pdf_extractor.extract_text_from_bytes(
                file_bytes
            )
            if len(page_contents) > MAX_PDF_PAGES:
                logger.info(
                    f"File {file.id} - {file.file_name} has more than 50 pages, skipping vectorization"
                )
                return

            async def insert_page(idx: int, page_content: str) -> None:
                await self.vector_repository.insert_document(
                    file.id,
                    file.file_name,
                    page_content,
                    page_number=idx + 1,
                )

            batch_size = 5
            for start in range(0, len(page_contents), batch_size):
                batch = page_contents[start : start + batch_size]
                batch_tasks = [
                    insert_page(i + start, content) for i, content in enumerate(batch)
                ]
                _ = await gather(*batch_tasks)

    async def archive_file(self, file_id: UUID) -> bool:
        return await self.repository.archive(file_id)

    async def delete_file(self, file_id: UUID) -> bool:
        file = await self.repository.get_by_id(file_id)
        if not file:
            return False
        await self.upload_service.delete_file(file.full_path)
        return await self.repository.delete(file_id)

    async def get_presigned_url(self, file_id: UUID) -> str | None:
        file = await self.repository.get_by_id(file_id)
        if not file:
            return None
        return await self.upload_service.get_presigned_url(file.full_path)

    async def find_by_linked_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> list[File]:
        return await self.repository.find_by_linked_entity(entity_type, entity_id)
