"""GraphQL response type for Order."""

from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission.orders.order import Order

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class OrderResponse(DTOMixin[Order]):
    id: UUID
    entry_date: datetime
    order_number: str
    status: int
    balance_id: UUID | None
    factory_id: UUID | None
    sold_to_customer_id: UUID | None
    bill_to_customer_id: UUID | None
    job_name: str | None
    entity_date: date
    ship_date: date | None
    due_date: date
    fact_so_number: str | None
    user_owner_ids: list[UUID]
    quote_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: Order) -> Self:
        return cls(
            id=model.id,
            entry_date=model.entry_date,
            order_number=model.order_number,
            status=model.status,
            balance_id=model.balance_id,
            factory_id=model.factory_id,
            sold_to_customer_id=model.sold_to_customer_id,
            bill_to_customer_id=model.bill_to_customer_id,
            job_name=model.job_name,
            entity_date=model.entity_date,
            ship_date=model.ship_date,
            due_date=model.due_date,
            fact_so_number=model.fact_so_number,
            user_owner_ids=model.user_owner_ids,
            quote_id=model.quote_id,
        )

    @strawberry.field
    def url(self) -> str:
        return f"/cm/orders/list/{self.id}"
