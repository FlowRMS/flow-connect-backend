from datetime import date
from uuid import UUID

import strawberry
from commons.auth import AuthInfo
from commons.db.v6 import AutoNumberEntityType
from commons.db.v6.commission.orders import Order, OrderDetail
from commons.db.v6.crm.links.entity_type import EntityType

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.auto_numbers.services.auto_number_settings_service import (
    AutoNumberSettingsService,
)
from app.graphql.orders.factories.order_factory import OrderFactory
from app.graphql.orders.repositories.orders_repository import OrdersRepository
from app.graphql.orders.strawberry.order_input import OrderInput
from app.graphql.orders.strawberry.quote_detail_to_order_input import (
    QuoteDetailToOrderDetailInput,
)
from app.graphql.orders.validators import validate_quote_details_same_factory
from app.graphql.quotes.repositories.quotes_repository import QuotesRepository


class OrderService:
    def __init__(
        self,
        repository: OrdersRepository,
        quotes_repository: QuotesRepository,
        auto_number_settings_service: AutoNumberSettingsService,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.quotes_repository = quotes_repository
        self.auto_number_settings_service = auto_number_settings_service
        self.auth_info = auth_info

    async def check_order_exists(
        self, order_number: str, customer_id: UUID | None = None
    ) -> bool:
        return await self.repository.order_number_exists(order_number, customer_id)

    async def find_by_order_number(
        self, order_number: str, customer_id: UUID
    ) -> Order | None:
        return await self.repository.find_by_order_number(order_number, customer_id)

    async def find_order_by_id(self, order_id: UUID) -> Order:
        return await self.repository.find_order_by_id(order_id)

    async def create_order(self, order_input: OrderInput) -> Order:
        if self.auto_number_settings_service.needs_generation(order_input.order_number):
            order_input.order_number = (
                await self.auto_number_settings_service.generate_number(
                    AutoNumberEntityType.ORDER
                )
            )

        if await self.repository.order_number_exists(
            order_input.order_number, order_input.sold_to_customer_id
        ):
            raise NameAlreadyExistsError(order_input.order_number)

        order = order_input.to_orm_model()
        return await self.repository.create_with_balance(order)

    def _merge_order_from_input(
        self, existing_order: Order, order_input: OrderInput
    ) -> Order:
        existing_by_item = {d.item_number: d for d in existing_order.details}
        result_details: list[OrderDetail] = []

        for new_d in order_input.details:
            new_detail = new_d.to_orm_model()
            if new_d.item_number in existing_by_item:
                existing_d = existing_by_item.pop(new_d.item_number)
                new_detail.id = existing_d.id
            new_detail.order_id = existing_order.id
            result_details.append(new_detail)

        for unchanged in existing_by_item.values():
            result_details.append(unchanged)

        existing_order.entity_date = order_input.entity_date
        existing_order.due_date = order_input.due_date
        existing_order.bill_to_customer_id = order_input.optional_field(
            order_input.bill_to_customer_id
        )
        existing_order.shipping_terms = order_input.optional_field(
            order_input.shipping_terms
        )
        existing_order.freight_terms = order_input.optional_field(
            order_input.freight_terms
        )
        existing_order.mark_number = order_input.optional_field(order_input.mark_number)
        existing_order.ship_date = order_input.optional_field(order_input.ship_date)
        existing_order.projected_ship_date = order_input.optional_field(
            order_input.projected_ship_date
        )
        existing_order.fact_so_number = order_input.optional_field(
            order_input.fact_so_number
        )
        existing_order.quote_id = order_input.optional_field(order_input.quote_id)
        if order_input.order_type != strawberry.UNSET:
            existing_order.order_type = order_input.order_type
        existing_order.details = result_details
        return existing_order

    async def create_order_or_merge(self, order_input: OrderInput) -> Order:
        existing = await self.repository.find_by_order_number_with_details(
            order_input.order_number, order_input.sold_to_customer_id
        )
        if existing:
            merged = self._merge_order_from_input(existing, order_input)
            return await self.repository.update_with_balance(merged)
        return await self.create_order(order_input)

    async def create_orders_bulk(self, order_inputs: list[OrderInput]) -> list[Order]:
        if not order_inputs:
            return []

        order_customer_pairs = [
            (inp.order_number, inp.sold_to_customer_id) for inp in order_inputs
        ]
        existing_orders = await self.repository.find_orders_by_number_customer_pairs(
            order_customer_pairs
        )
        existing_map = {
            (o.order_number, o.sold_to_customer_id): o for o in existing_orders
        }

        to_create: list[OrderInput] = []
        to_create_indices: list[int] = []
        results: list[Order | None] = [None] * len(order_inputs)

        for i, inp in enumerate(order_inputs):
            key = (inp.order_number, inp.sold_to_customer_id)
            if key in existing_map:
                merged = self._merge_order_from_input(existing_map[key], inp)
                results[i] = await self.repository.update_with_balance(merged)
            else:
                to_create.append(inp)
                to_create_indices.append(i)

        if not to_create:
            return [r for r in results if r is not None]

        orders = [inp.to_orm_model() for inp in to_create]
        details_list = [order.details for order in orders]
        balances = await self.repository.create_balances_bulk(details_list)
        for order, balance in zip(orders, balances, strict=True):
            order.balance_id = balance.id
        created = await self.repository.create_bulk(orders)
        for j, idx in enumerate(to_create_indices):
            results[idx] = created[j]
        return [r for r in results if r is not None]

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

    async def find_by_factory_id(
        self, factory_id: UUID, limit: int = 25
    ) -> list[Order]:
        return await self.repository.find_by_factory_id(factory_id, limit)

    async def duplicate_order(
        self,
        order_id: UUID,
        new_order_number: str,
        new_sold_to_customer_id: UUID,
    ) -> Order:
        existing_order = await self.repository.find_order_by_id(order_id)

        if self.auto_number_settings_service.needs_generation(new_order_number):
            new_order_number = await self.auto_number_settings_service.generate_number(
                AutoNumberEntityType.ORDER
            )

        if await self.repository.order_number_exists(
            new_order_number, new_sold_to_customer_id
        ):
            raise NameAlreadyExistsError(new_order_number)

        new_order = OrderFactory.from_order(
            existing_order, new_order_number, new_sold_to_customer_id
        )
        return await self.repository.create_with_balance(new_order)

    async def create_order_from_quote(
        self,
        quote_id: UUID,
        order_number: str,
        factory_id: UUID,
        due_date: date | None = None,
        quote_details_inputs: list[QuoteDetailToOrderDetailInput] | None = None,
    ) -> Order:
        quote = await self.quotes_repository.find_quote_by_id(quote_id)

        validate_quote_details_same_factory(quote, quote_details_inputs)

        if self.auto_number_settings_service.needs_generation(order_number):
            order_number = await self.auto_number_settings_service.generate_number(
                AutoNumberEntityType.ORDER
            )

        if await self.repository.order_number_exists(
            order_number, quote.sold_to_customer_id
        ):
            raise NameAlreadyExistsError(order_number)

        order = OrderFactory.from_quote(
            quote, order_number, factory_id, due_date, quote_details_inputs
        )
        created_order = await self.repository.create_with_balance(order)

        if quote_details_inputs:
            quote_detail_ids = [inp.quote_detail_id for inp in quote_details_inputs]
            await self.quotes_repository.update_detail_order_ids(
                detail_ids=quote_detail_ids,
                order_id=created_order.id,
            )

        return created_order

    async def get_existing_orders(
        self, order_customer_pairs: list[tuple[str, UUID]]
    ) -> list[Order]:
        return await self.repository.get_existing_orders(order_customer_pairs)

    async def find_by_sold_to_customer_id(self, customer_id: UUID) -> list[Order]:
        return await self.repository.find_by_sold_to_customer_id(customer_id)
