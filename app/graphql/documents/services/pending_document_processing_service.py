from uuid import UUID

from commons.db.v6.ai.documents.pending_document_processing import (
    PendingDocumentProcessing,
)

from app.errors.common_errors import NotFoundError
from app.graphql.documents.repositories.pending_document_processing_repository import (
    PendingDocumentProcessingRepository,
)
from app.graphql.documents.strawberry.pending_document_processing_input import (
    PendingDocumentProcessingInput,
)


class PendingDocumentProcessingService:
    def __init__(
        self,
        repository: PendingDocumentProcessingRepository,
    ) -> None:
        super().__init__()
        self.repository = repository

    async def get_by_pending_document_id(
        self,
        pending_document_id: UUID,
    ) -> list[PendingDocumentProcessing]:
        return await self.repository.get_by_pending_document_id(pending_document_id)

    async def get_by_id(self, processing_id: UUID) -> PendingDocumentProcessing:
        processing = await self.repository.get_by_id(processing_id)
        if not processing:
            raise NotFoundError(str(processing_id))
        return processing

    async def update(
        self,
        processing_id: UUID,
        input: PendingDocumentProcessingInput,
    ) -> PendingDocumentProcessing:
        if not await self.repository.exists(processing_id):
            raise NotFoundError(str(processing_id))

        processing = input.to_orm_model()
        processing.id = processing_id
        return await self.repository.update(processing)

    async def delete(self, processing_id: UUID) -> bool:
        if not await self.repository.exists(processing_id):
            raise NotFoundError(str(processing_id))
        return await self.repository.delete(processing_id)
