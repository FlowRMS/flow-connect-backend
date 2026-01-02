from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.commission.orders import Order, OrderAcknowledgement, OrderDetail
from commons.db.v6.core import Customer, Factory
from commons.db.v6.core.products import Product
from sqlalchemy import Select, func, literal, select
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.orders.strawberry.order_acknowledgement_landing_page_response import (
    OrderAcknowledgementLandingPageResponse,
)


class OrderAcknowledgementRepository(BaseRepository[OrderAcknowledgement]):
    landing_model = OrderAcknowledgementLandingPageResponse
    rbac_resource: RbacResourceEnum | None = None

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            OrderAcknowledgement,
        )

    def paginated_stmt(self) -> Select[Any]:
        empty_array = literal([]).cast(ARRAY(PG_UUID))

        user_ids_expr = func.coalesce(
            func.array_agg(OrderAcknowledgement.created_by_id.distinct()),
            empty_array,
        ).label("user_ids")

        return (
            select(
                OrderAcknowledgement.id,
                OrderAcknowledgement.created_at,
                User.full_name.label("created_by"),
                OrderAcknowledgement.order_acknowledgement_number,
                OrderAcknowledgement.entity_date,
                OrderAcknowledgement.quantity,
                OrderAcknowledgement.ship_date,
                OrderAcknowledgement.creation_type,
                Order.order_number,
                Order.entity_date.label("order_entity_date"),
                Customer.company_name.label("sold_to_customer_name"),
                Factory.title.label("factory_name"),
                Product.factory_part_number.label("product_name"),
                OrderDetail.item_number,
                user_ids_expr,
            )
            .select_from(OrderAcknowledgement)
            .options(lazyload("*"))
            .join(User, User.id == OrderAcknowledgement.created_by_id)
            .join(Order, Order.id == OrderAcknowledgement.order_id)
            .join(OrderDetail, OrderDetail.id == OrderAcknowledgement.order_detail_id)
            .join(Customer, Customer.id == Order.sold_to_customer_id)
            .join(Factory, Factory.id == Order.factory_id)
            .outerjoin(Product, Product.id == OrderDetail.product_id)
            .group_by(
                OrderAcknowledgement.id,
                OrderAcknowledgement.created_at,
                User.full_name,
                OrderAcknowledgement.order_acknowledgement_number,
                OrderAcknowledgement.entity_date,
                OrderAcknowledgement.quantity,
                OrderAcknowledgement.ship_date,
                OrderAcknowledgement.creation_type,
                Order.order_number,
                Order.entity_date,
                Customer.company_name,
                Factory.title,
                Product.factory_part_number,
                OrderDetail.item_number,
            )
        )

    async def find_by_order_id(self, order_id: UUID) -> list[OrderAcknowledgement]:
        stmt = (
            select(OrderAcknowledgement)
            .options(lazyload("*"))
            .where(OrderAcknowledgement.order_id == order_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_order_detail_id(
        self, order_detail_id: UUID
    ) -> list[OrderAcknowledgement]:
        stmt = (
            select(OrderAcknowledgement)
            .options(lazyload("*"))
            .where(OrderAcknowledgement.order_detail_id == order_detail_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
