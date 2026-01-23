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
from app.graphql.v2.core.deliveries.strawberry.inputs import DeliveryDocumentInput


@strawberry.type
class DeliveryDocumentsMutations:
    """GraphQL mutations for DeliveryDocument entity."""

    @strawberry.mutation
    @inject
    async def create_delivery_document(
        self,
        input: DeliveryDocumentInput,
        service: Injected[DeliveryDocumentService],
    ) -> DeliveryDocumentResponse:
        document = await service.create(input)
        return DeliveryDocumentResponse.from_orm_model(document)

    @strawberry.mutation
    @inject
    async def update_delivery_document(
        self,
        id: UUID,
        input: DeliveryDocumentInput,
        service: Injected[DeliveryDocumentService],
    ) -> DeliveryDocumentResponse:
        document = await service.update(id, input)
        return DeliveryDocumentResponse.from_orm_model(document)

    @strawberry.mutation
    @inject
    async def delete_delivery_document(
        self,
        id: UUID,
        service: Injected[DeliveryDocumentService],
    ) -> bool:
        return await service.delete(id)
