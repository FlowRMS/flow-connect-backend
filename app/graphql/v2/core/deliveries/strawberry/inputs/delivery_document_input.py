
from uuid import UUID

import strawberry
from commons.db.v6 import DeliveryDocument
from commons.db.v6.warehouse.deliveries.delivery_enums import DeliveryDocumentType

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class DeliveryDocumentInput(BaseInputGQL[DeliveryDocument]):
    """Input type for creating/updating delivery documents."""

    delivery_id: UUID
    file_id: UUID
    doc_type: DeliveryDocumentType
    uploaded_by_id: UUID | None = None
    notes: str | None = None

    def to_orm_model(self) -> DeliveryDocument:
        return DeliveryDocument(
            delivery_id=self.delivery_id,
            file_id=self.file_id,
            doc_type=self.doc_type,
            uploaded_by_id=self.uploaded_by_id,
            notes=self.notes,
        )
