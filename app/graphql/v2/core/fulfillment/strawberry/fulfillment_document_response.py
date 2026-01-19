from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import FulfillmentDocument

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.fulfillment.strawberry.enums import FulfillmentDocumentType


@strawberry.type
class FulfillmentDocumentResponse(DTOMixin[FulfillmentDocument]):
    _instance: strawberry.Private[FulfillmentDocument]
    id: UUID
    document_type: FulfillmentDocumentType
    file_name: str
    file_url: str
    file_size: int | None
    mime_type: str | None
    notes: str | None
    uploaded_at: datetime
    created_at: datetime
    created_by_id: UUID
    file_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: FulfillmentDocument) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            document_type=model.document_type,
            file_name=model.file_name,
            file_url=model.file_url,
            file_size=model.file_size,
            mime_type=model.mime_type,
            notes=model.notes,
            uploaded_at=model.uploaded_at,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
            file_id=model.file_id,
        )

    @strawberry.field
    def uploaded_by_name(self) -> str:
        """Get uploaded by user name - relationship is eager-loaded."""
        return self._instance.uploaded_by_user.full_name if self._instance.uploaded_by_user else ""
