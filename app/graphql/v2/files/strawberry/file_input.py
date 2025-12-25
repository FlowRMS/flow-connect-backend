from uuid import UUID

import strawberry
from strawberry.file_uploads import Upload


@strawberry.input
class FileUploadInput:
    file: Upload
    file_name: str
    folder_id: UUID | None = None
    folder_path: str | None = None


@strawberry.input
class MultiFileUploadInput:
    files: list[Upload]
    file_names: list[str]
    folder_id: UUID | None = None
    folder_path: str | None = None
