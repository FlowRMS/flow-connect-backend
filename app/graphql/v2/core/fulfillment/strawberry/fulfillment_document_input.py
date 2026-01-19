"""Input types for fulfillment documents."""

from datetime import UTC, datetime
from typing import Optional
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import FulfillmentDocument
from strawberry.file_uploads import Upload

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.v2.core.fulfillment.strawberry.enums import FulfillmentDocumentType


@strawberry.input
class AddDocumentInput(BaseInputGQL[FulfillmentDocument]):
    """Input for adding a document to a fulfillment order."""

    fulfillment_order_id: UUID
    document_type: FulfillmentDocumentType
    file_name: str
    file_url: str
    file_size: int | None = None
    mime_type: str | None = None
    notes: str | None = None

    def to_orm_model(self) -> FulfillmentDocument:
        document = FulfillmentDocument(
            document_type=self.document_type,
            file_name=self.file_name,
            file_url=self.file_url,
            file_size=self.file_size,
            mime_type=self.mime_type,
            notes=self.notes,
            uploaded_at=datetime.now(UTC).replace(tzinfo=None),
        )
        document.fulfillment_order_id = self.fulfillment_order_id
        return document


@strawberry.input
class UploadDocumentInput:
    """Input for uploading a document file to a fulfillment order."""

    fulfillment_order_id: UUID
    document_type: FulfillmentDocumentType
    file: Upload
    notes: Optional[str] = None
