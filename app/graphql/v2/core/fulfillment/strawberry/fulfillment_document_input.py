from typing import Optional
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import FulfillmentDocumentType
from strawberry.file_uploads import Upload


@strawberry.input
class AddDocumentInput:
    """Input for adding a document to a fulfillment order."""

    fulfillment_order_id: UUID
    document_type: FulfillmentDocumentType
    file_name: str
    file_url: str
    file_size: int | None = None
    mime_type: str | None = None
    notes: str | None = None


@strawberry.input
class UploadDocumentInput:
    """Input for uploading a document file to a fulfillment order."""

    fulfillment_order_id: UUID
    document_type: FulfillmentDocumentType
    file: Upload
    notes: Optional[str] = None
