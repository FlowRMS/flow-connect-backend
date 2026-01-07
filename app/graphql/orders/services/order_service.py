from datetime import date
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.commission.orders import Order
from commons.db.v6.crm.links.entity_type import EntityType

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.orders.factories.order_factory import OrderFactory
from app.graphql.orders.repositories.orders_repository import OrdersRepository
from app.graphql.orders.strawberry.order_input import OrderInput
from app.graphql.quotes.repositories.quotes_repository import QuotesRepository


class OrderService:
    def __init__(
        self,
        repository: OrdersRepository,
        quotes_repository: QuotesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.quotes_repository = quotes_repository
        self.auth_info = auth_info

    async def find_order_by_id(self, order_id: UUID) -> Order:
        return await self.repository.find_order_by_id(order_id)

    async def create_order(self, order_input: OrderInput) -> Order:
        if await self.repository.order_number_exists(order_input.order_number):
            raise NameAlreadyExistsError(order_input.order_number)

        order = order_input.to_orm_model()
        return await self.repository.create_with_balance(order)

    async def update_order(self, order_input: OrderInput) -> Order:
        if order_input.id is None:
            raise ValueError("ID must be provided for update")

        order = order_input.to_orm_model()
        order.id = order_input.id
        return await self.repository.update_with_balance(order)

    async def delete_order(self, order_id: UUID) -> bool:
        if not await self.repository.exists(order_id):
            raise NotFoundError(str(order_id))
        return await self.repository.delete(order_id)

    async def search_orders(self, search_term: str, limit: int = 20) -> list[Order]:
        return await self.repository.search_by_order_number(search_term, limit)

    async def find_orders_by_job_id(self, job_id: UUID) -> list[Order]:
        return await self.repository.find_by_job_id(job_id)

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Order]:
        return await self.repository.find_by_entity(entity_type, entity_id)

    async def create_order_from_quote(
        self,
        quote_id: UUID,
        order_number: str,
        factory_id: UUID,
        due_date: date | None = None,
        quote_detail_ids: list[UUID] | None = None,
    ) -> Order:
        quote = await self.quotes_repository.find_quote_by_id(quote_id)

        if await self.repository.order_number_exists(order_number):
            raise NameAlreadyExistsError(order_number)

        order = OrderFactory.from_quote(quote, order_number, factory_id, due_date)
        created_order = await self.repository.create_with_balance(order)

        if quote_detail_ids:
            await self.quotes_repository.update_detail_order_ids(
                detail_ids=quote_detail_ids,
                order_id=created_order.id,
            )

        return created_order
