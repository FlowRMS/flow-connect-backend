from uuid import UUID

import strawberry
from commons.db.v6.fulfillment.enums import FulfillmentDocumentType
from strawberry.file_uploads import Upload


@strawberry.input
class UploadDocumentInput:
    """Input for uploading a document file to a fulfillment order."""

    fulfillment_order_id: UUID
    document_type: FulfillmentDocumentType
    file: Upload
    notes: str | None = None
