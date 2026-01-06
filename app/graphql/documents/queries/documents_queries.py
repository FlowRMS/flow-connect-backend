from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.documents.services.pending_document_processing_service import (
    PendingDocumentProcessingService,
)
from app.graphql.documents.strawberry.pending_document_processing_type import (
    PendingDocumentProcessingType,
)
from app.graphql.inject import inject


@strawberry.type
class DocumentsQueries:
    @strawberry.field
    @inject
    async def pending_document_processings(
        self,
        pending_document_id: UUID,
        service: Injected[PendingDocumentProcessingService],
    ) -> list[PendingDocumentProcessingType]:
        processings = await service.get_by_pending_document_id(pending_document_id)
        return [PendingDocumentProcessingType.from_model(p) for p in processings]
