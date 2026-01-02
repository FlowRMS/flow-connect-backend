from datetime import datetime
from enum import Enum
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.files import File, FileType

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.enum
class FileTypeEnum(Enum):
    DOCUMENT = "DOCUMENT"
    IMAGE = "IMAGE"
    PDF = "PDF"
    SPREADSHEET = "SPREADSHEET"
    PRESENTATION = "PRESENTATION"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    ARCHIVE = "ARCHIVE"
    OTHER = "OTHER"


FILE_TYPE_MAP: dict[FileType, FileTypeEnum] = {
    FileType.DOCUMENT: FileTypeEnum.DOCUMENT,
    FileType.IMAGE: FileTypeEnum.IMAGE,
    FileType.PDF: FileTypeEnum.PDF,
    FileType.SPREADSHEET: FileTypeEnum.SPREADSHEET,
    FileType.PRESENTATION: FileTypeEnum.PRESENTATION,
    FileType.VIDEO: FileTypeEnum.VIDEO,
    FileType.AUDIO: FileTypeEnum.AUDIO,
    FileType.ARCHIVE: FileTypeEnum.ARCHIVE,
    FileType.OTHER: FileTypeEnum.OTHER,
}


def file_type_to_enum(file_type: FileType | None) -> FileTypeEnum | None:
    if file_type is None:
        return None
    return FILE_TYPE_MAP.get(file_type, FileTypeEnum.OTHER)


@strawberry.type
class FileLiteResponse(DTOMixin[File]):
    _instance: strawberry.Private[File]
    id: UUID
    created_at: datetime
    file_name: str
    file_path: str
    file_size: int
    file_type: FileTypeEnum | None
    file_sha: str | None
    archived: bool
    folder_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: File) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            file_name=model.file_name,
            file_path=model.file_path,
            file_size=model.file_size,
            file_type=file_type_to_enum(model.file_type),
            file_sha=model.file_sha,
            archived=model.archived,
            folder_id=model.folder_id,
        )


@strawberry.type
class FileResponse(FileLiteResponse):
    @strawberry.field
    def created_by(self) -> UserResponse:
        return UserResponse.from_orm_model(self._instance.created_by)
