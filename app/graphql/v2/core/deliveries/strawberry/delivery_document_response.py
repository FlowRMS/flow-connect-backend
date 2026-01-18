
from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryDocument
from commons.db.v6.warehouse.deliveries.delivery_enums import DeliveryDocumentType

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class DeliveryDocumentResponse(DTOMixin[DeliveryDocument]):
    """Response type for delivery documents."""

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
        return cls(
            _instance=model,
            id=model.id,
            delivery_id=model.delivery_id,
            file_id=model.file_id,
            name=model.name,
            doc_type=model.doc_type,
            file_url=model.file_url,
            mime_type=model.mime_type,
            file_size=model.file_size,
            uploaded_by_id=model.uploaded_by_id,
            uploaded_at=model.uploaded_at,
            notes=model.notes,
        )
