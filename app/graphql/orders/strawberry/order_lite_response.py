from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission.orders import (
    Order,
    OrderHeaderStatus,
    OrderStatus,
    OrderType,
)
from commons.db.v6.common.creation_type import CreationType

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class OrderLiteResponse(DTOMixin[Order]):
    _instance: strawberry.Private[Order]
    id: UUID
    created_at: datetime
    created_by_id: UUID
    order_number: str
    entity_date: date
    due_date: date
    status: OrderStatus
    header_status: OrderHeaderStatus
    order_type: OrderType
    published: bool
    creation_type: CreationType
    sold_to_customer_id: UUID
    bill_to_customer_id: UUID | None
    factory_id: UUID | None
    shipping_terms: str | None
    freight_terms: str | None
    mark_number: str | None
    ship_date: date | None
    projected_ship_date: date | None
    fact_so_number: str | None
    quote_id: UUID | None
    balance_id: UUID

    @classmethod
    def from_orm_model(cls, model: Order) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
            order_number=model.order_number,
            entity_date=model.entity_date,
            due_date=model.due_date,
            status=model.status,
            header_status=model.header_status,
            order_type=model.order_type,
            published=model.published,
            creation_type=model.creation_type,
            sold_to_customer_id=model.sold_to_customer_id,
            bill_to_customer_id=model.bill_to_customer_id,
            factory_id=model.factory_id,
            shipping_terms=model.shipping_terms,
            freight_terms=model.freight_terms,
            mark_number=model.mark_number,
            ship_date=model.ship_date,
            projected_ship_date=model.projected_ship_date,
            fact_so_number=model.fact_so_number,
            quote_id=model.quote_id,
            balance_id=model.balance_id,
        )

    @strawberry.field
    def url(self) -> str:
        return f"/cm/orders/list/{self.id}"
