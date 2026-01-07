from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.ai.documents.enums.processing_result_status import (
    ProcessingResultStatus,
)
from commons.db.v6.ai.documents.pending_document_processing import (
    PendingDocumentProcessing,
)


@strawberry.type
class PendingDocumentProcessingType:
    id: UUID
    pending_document_id: UUID
    entity_id: UUID | None
    status: ProcessingResultStatus
    dto_json: strawberry.scalars.JSON | None
    error_message: str | None

    @classmethod
    def from_model(
        cls,
        model: PendingDocumentProcessing,
    ) -> Self:
        return cls(
            id=model.id,
            pending_document_id=model.pending_document_id,
            entity_id=model.entity_id,
            status=model.status,
            dto_json=model.dto_json,
            error_message=model.error_message,
        )
