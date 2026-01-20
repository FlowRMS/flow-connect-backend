
from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryDocument
from commons.db.v6.files import FileType
from commons.db.v6.warehouse.deliveries.delivery_enums import DeliveryDocumentType

from app.core.db.adapters.dto import DTOMixin


FILE_TYPE_MIME_MAP: dict[FileType, str] = {
    FileType.IMAGE: "image/*",
    FileType.PDF: "application/pdf",
    FileType.DOCUMENT: "application/octet-stream",
    FileType.SPREADSHEET: "application/vnd.ms-excel",
    FileType.PRESENTATION: "application/vnd.ms-powerpoint",
    FileType.VIDEO: "video/*",
    FileType.AUDIO: "audio/*",
    FileType.ARCHIVE: "application/zip",
    FileType.OTHER: "application/octet-stream",
}


def file_type_to_mime(file_type: FileType | None) -> str:
    if file_type is None:
        return "application/octet-stream"
    return FILE_TYPE_MIME_MAP.get(file_type, "application/octet-stream")


@strawberry.type
class DeliveryDocumentLiteResponse(DTOMixin[DeliveryDocument]):
    """Lite response type for delivery documents - used for list queries."""

    _instance: strawberry.Private[DeliveryDocument]
    id: UUID
    delivery_id: UUID
    file_id: UUID | None
    name: str
    doc_type: DeliveryDocumentType
    file_url: str
    mime_type: str
    file_size: int | None
    uploaded_by_id: UUID | None
    uploaded_at: datetime
    notes: str | None

    @classmethod
    def from_orm_model(cls, model: DeliveryDocument) -> Self:
        file = model.file
        return cls(
            _instance=model,
            id=model.id,
            delivery_id=model.delivery_id,
            file_id=model.file_id,
            name=file.file_name if file else "",
            doc_type=model.doc_type,
            file_url=file.file_path if file and file.file_path else "",
            mime_type=file_type_to_mime(file.file_type) if file else "application/octet-stream",
            file_size=file.file_size if file else None,
            uploaded_by_id=model.uploaded_by_id,
            uploaded_at=model.uploaded_at,
            notes=model.notes,
        )


@strawberry.type
class DeliveryDocumentResponse(DeliveryDocumentLiteResponse):
    """Full response type for delivery documents."""

    pass
