from uuid import UUID

from commons.db.v6.core.customers.factory_customer_reference import (
    FactoryCustomerReference,
)

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.customers.repositories.factory_customer_reference_repository import (
    FactoryCustomerReferenceRepository,
)
from app.graphql.v2.core.customers.strawberry.factory_customer_reference_input import (
    FactoryCustomerReferenceInput,
)


class FactoryCustomerReferenceService:
    def __init__(self, repository: FactoryCustomerReferenceRepository) -> None:
        super().__init__()
        self.repository = repository

    async def get_by_id(self, reference_id: UUID) -> FactoryCustomerReference:
        ref = await self.repository.get_by_id_with_relations(reference_id)
        if not ref:
            raise NotFoundError(
                f"FactoryCustomerReference with id {reference_id} not found"
            )
        return ref

    async def list_by_factory(
        self,
        factory_id: UUID,
    ) -> list[FactoryCustomerReference]:
        return await self.repository.list_by_factory(factory_id)

    async def get_by_customer_and_factory(
        self,
        customer_id: UUID,
        factory_id: UUID,
    ) -> FactoryCustomerReference | None:
        return await self.repository.get_by_customer_and_factory(
            customer_id, factory_id
        )

    async def create(
        self,
        ref_input: FactoryCustomerReferenceInput,
    ) -> FactoryCustomerReference:
        ref = await self.repository.create(ref_input.to_orm_model())
        return await self.get_by_id(ref.id)

    async def update(
        self,
        reference_id: UUID,
        ref_input: FactoryCustomerReferenceInput,
    ) -> FactoryCustomerReference:
        existing = await self.repository.get_by_id(reference_id)
        if not existing:
            raise NotFoundError(
                f"FactoryCustomerReference with id {reference_id} not found"
            )

        ref = ref_input.to_orm_model()
        ref.id = reference_id
        _ = await self.repository.update(ref)
        return await self.get_by_id(reference_id)

    async def delete(self, reference_id: UUID) -> bool:
        if not await self.repository.exists(reference_id):
            raise NotFoundError(
                f"FactoryCustomerReference with id {reference_id} not found"
            )
        return await self.repository.delete(reference_id)
