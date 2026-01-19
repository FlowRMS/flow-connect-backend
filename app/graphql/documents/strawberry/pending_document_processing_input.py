from uuid import UUID

import strawberry
from commons.db.v6.ai.documents.enums.processing_result_status import (
    ProcessingResultStatus,
)
from commons.db.v6.ai.documents.pending_document_processing import (
    PendingDocumentProcessing,
)


@strawberry.input
class PendingDocumentProcessingInput:
    pending_document_id: UUID
    entity_id: UUID | None = None
    status: ProcessingResultStatus
    dto_json: strawberry.scalars.JSON | None = None
    error_message: str | None = None

    def to_orm_model(self) -> PendingDocumentProcessing:
        return PendingDocumentProcessing(
            pending_document_id=self.pending_document_id,
            entity_id=self.entity_id,
            status=self.status,
            dto_json=self.dto_json,
            error_message=self.error_message,
        )
