from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.customers.services.factory_customer_reference_service import (
    FactoryCustomerReferenceService,
)
from app.graphql.v2.core.customers.strawberry.factory_customer_reference_input import (
    FactoryCustomerReferenceInput,
)
from app.graphql.v2.core.customers.strawberry.factory_customer_reference_response import (
    FactoryCustomerReferenceResponse,
)


@strawberry.type
class FactoryCustomerReferenceMutations:
    @strawberry.mutation
    @inject
    async def create_factory_customer_reference(
        self,
        input: FactoryCustomerReferenceInput,
        service: Injected[FactoryCustomerReferenceService],
    ) -> FactoryCustomerReferenceResponse:
        ref = await service.create(input)
        return FactoryCustomerReferenceResponse.from_orm_model(ref)

    @strawberry.mutation
    @inject
    async def update_factory_customer_reference(
        self,
        id: UUID,
        input: FactoryCustomerReferenceInput,
        service: Injected[FactoryCustomerReferenceService],
    ) -> FactoryCustomerReferenceResponse:
        ref = await service.update(id, input)
        return FactoryCustomerReferenceResponse.from_orm_model(ref)

    @strawberry.mutation
    @inject
    async def delete_factory_customer_reference(
        self,
        id: UUID,
        service: Injected[FactoryCustomerReferenceService],
    ) -> bool:
        return await service.delete(id)
