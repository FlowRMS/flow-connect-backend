from uuid import UUID

from commons.db.v6 import Customer
from commons.db.v6.crm.links.entity_type import EntityType
from sqlalchemy.orm import joinedload

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.customers.repositories.customers_repository import (
    CustomersRepository,
)
from app.graphql.v2.core.customers.strawberry.customer_input import CustomerInput


class CustomerService:
    def __init__(
        self,
        repository: CustomersRepository,
    ) -> None:
        super().__init__()
        self.repository = repository

    async def get_by_id(self, customer_id: UUID) -> Customer:
        customer = await self.repository.get_by_id(
            customer_id,
            options=[
                joinedload(Customer.created_by),
                joinedload(Customer.outside_reps),
                joinedload(Customer.inside_reps),
            ],
        )
        if not customer:
            raise NotFoundError(f"Customer with id {customer_id} not found")
        return customer

    async def create(self, customer_input: CustomerInput) -> Customer:
        customer = await self.repository.create(customer_input.to_orm_model())
        return await self.get_by_id(customer.id)

    async def update(
        self, customer_id: UUID, customer_input: CustomerInput
    ) -> Customer:
        customer = customer_input.to_orm_model()
        customer.id = customer_id
        _ = await self.repository.update(customer)
        return await self.get_by_id(customer_id)

    async def delete(self, customer_id: UUID) -> bool:
        if not await self.repository.exists(customer_id):
            raise NotFoundError(f"Customer with id {customer_id} not found")
        return await self.repository.delete(customer_id)

    async def search_customers(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[Customer]:
        return await self.repository.search_by_company_name(
            search_term, published, limit
        )

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Customer]:
        return await self.repository.find_by_entity(entity_type, entity_id)
