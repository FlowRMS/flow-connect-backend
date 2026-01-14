
from datetime import datetime
import mimetypes
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryDocument

from app.core.db.adapters.dto import DTOMixin

from .delivery_enums import DeliveryDocumentTypeGQL


@strawberry.type
class DeliveryDocumentResponse(DTOMixin[DeliveryDocument]):
    """Response type for delivery documents."""

    _instance: strawberry.Private[DeliveryDocument]
    id: UUID
    delivery_id: UUID
    name: str
    doc_type: DeliveryDocumentTypeGQL
    file_url: str
    mime_type: str
    file_size: int | None
    uploaded_by_id: UUID | None
    uploaded_at: datetime
    notes: str | None

    @classmethod
    def from_orm_model(cls, model: DeliveryDocument) -> Self:
        file = model.file
        mime_type, _ = mimetypes.guess_type(file.file_name)
        return cls(
            _instance=model,
            id=model.id,
            delivery_id=model.delivery_id,
            name=file.file_name,
            doc_type=DeliveryDocumentTypeGQL(model.doc_type.value),
            file_url=file.full_path,
            mime_type=mime_type or "application/octet-stream",
            file_size=file.file_size,
            uploaded_by_id=model.uploaded_by_id,
            uploaded_at=model.uploaded_at,
            notes=model.notes,
        )
