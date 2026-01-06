
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.deliveries.services.delivery_document_service import (
    DeliveryDocumentService,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_document_response import (
    DeliveryDocumentResponse,
)


@strawberry.type
class DeliveryDocumentsQueries:
    """GraphQL queries for DeliveryDocument entity."""

    @strawberry.field
    @inject
    async def delivery_documents(
        self,
        delivery_id: UUID,
        service: Injected[DeliveryDocumentService],
    ) -> list[DeliveryDocumentResponse]:
        documents = await service.list_by_delivery(delivery_id)
        return DeliveryDocumentResponse.from_orm_model_list(documents)

    @strawberry.field
    @inject
    async def delivery_document(
        self,
        id: UUID,
        service: Injected[DeliveryDocumentService],
    ) -> DeliveryDocumentResponse:
        document = await service.get_by_id(id)
        return DeliveryDocumentResponse.from_orm_model(document)
