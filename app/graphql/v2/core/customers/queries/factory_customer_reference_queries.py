from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.customers.services.factory_customer_reference_service import (
    FactoryCustomerReferenceService,
)
from app.graphql.v2.core.customers.strawberry.factory_customer_reference_response import (
    FactoryCustomerReferenceResponse,
)


@strawberry.type
class FactoryCustomerReferenceQueries:
    @strawberry.field
    @inject
    async def factory_customer_reference(
        self,
        id: UUID,
        service: Injected[FactoryCustomerReferenceService],
    ) -> FactoryCustomerReferenceResponse:
        ref = await service.get_by_id(id)
        return FactoryCustomerReferenceResponse.from_orm_model(ref)

    @strawberry.field
    @inject
    async def list_factory_customer_references(
        self,
        factory_id: UUID,
        service: Injected[FactoryCustomerReferenceService],
    ) -> list[FactoryCustomerReferenceResponse]:
        refs = await service.list_by_factory(factory_id)
        return FactoryCustomerReferenceResponse.from_orm_model_list(refs)

    @strawberry.field
    @inject
    async def factory_customer_reference_by_customer(
        self,
        customer_id: UUID,
        factory_id: UUID,
        service: Injected[FactoryCustomerReferenceService],
    ) -> FactoryCustomerReferenceResponse | None:
        ref = await service.get_by_customer_and_factory(customer_id, factory_id)
        return FactoryCustomerReferenceResponse.from_orm_model_optional(ref)
