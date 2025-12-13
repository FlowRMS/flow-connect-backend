from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.core.customers.models import CustomerV2
from app.graphql.core.customers.repositories.customers_repository import (
    CustomersRepository,
)
from app.graphql.core.customers.strawberry.customer_input import CustomerInput
from app.graphql.links.models.entity_type import EntityType


class CustomerService:
    def __init__(
        self,
        repository: CustomersRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, customer_id: UUID) -> CustomerV2:
        customer = await self.repository.get_by_id(customer_id)
        if not customer:
            raise NotFoundError(f"CustomerV2 with id {customer_id} not found")
        return customer

    async def create(self, customer_input: CustomerInput) -> CustomerV2:
        return await self.repository.create(customer_input.to_orm_model())

    async def update(
        self, customer_id: UUID, customer_input: CustomerInput
    ) -> CustomerV2:
        customer = customer_input.to_orm_model()
        customer.id = customer_id
        return await self.repository.update(customer)

    async def delete(self, customer_id: UUID) -> bool:
        if not await self.repository.exists(customer_id):
            raise NotFoundError(f"CustomerV2 with id {customer_id} not found")
        return await self.repository.delete(customer_id)

    async def search_customers(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[CustomerV2]:
        return await self.repository.search_by_company_name(
            search_term, published, limit
        )

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[CustomerV2]:
        return await self.repository.find_by_entity(entity_type, entity_id)
