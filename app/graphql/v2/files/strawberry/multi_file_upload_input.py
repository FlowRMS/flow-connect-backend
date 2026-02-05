from uuid import UUID

import strawberry
from commons.db.v6.enums import DocumentEntityType
from strawberry.file_uploads import Upload


@strawberry.input
class MultiFileUploadInput:
    files: list[Upload]
    file_names: list[str]
    folder_id: UUID | None = None
    folder_path: str | None = None
    file_entity_type: DocumentEntityType | None = None
