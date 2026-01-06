
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import DeliveryDocument

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.deliveries.repositories.delivery_documents_repository import (
    DeliveryDocumentsRepository,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_input import (
    DeliveryDocumentInput,
)


class DeliveryDocumentService:
    """Service for delivery document operations."""

    def __init__(
        self,
        repository: DeliveryDocumentsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, document_id: UUID) -> DeliveryDocument:
        document = await self.repository.get_by_id(document_id)
        if not document:
            raise NotFoundError(
                f"Delivery document with id {document_id} not found"
            )
        return document

    async def list_by_delivery(self, delivery_id: UUID) -> list[DeliveryDocument]:
        return await self.repository.list_by_delivery(delivery_id)

    async def create(self, input: DeliveryDocumentInput) -> DeliveryDocument:
        return await self.repository.create(input.to_orm_model())

    async def update(
        self, document_id: UUID, input: DeliveryDocumentInput
    ) -> DeliveryDocument:
        if not await self.repository.exists(document_id):
            raise NotFoundError(
                f"Delivery document with id {document_id} not found"
            )
        document = input.to_orm_model()
        document.id = document_id
        return await self.repository.update(document)

    async def delete(self, document_id: UUID) -> bool:
        if not await self.repository.exists(document_id):
            raise NotFoundError(
                f"Delivery document with id {document_id} not found"
            )
        return await self.repository.delete(document_id)
