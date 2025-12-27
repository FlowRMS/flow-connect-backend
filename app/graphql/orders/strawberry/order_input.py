from datetime import date
from uuid import UUID

import strawberry
from commons.db.v6.commission.orders import (
    Order,
    OrderHeaderStatus,
    OrderStatus,
    OrderType,
)
from commons.db.v6.common.creation_type import CreationType

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.orders.strawberry.order_detail_input import OrderDetailInput
from app.graphql.orders.strawberry.order_inside_rep_input import OrderInsideRepInput


@strawberry.input
class OrderInput(BaseInputGQL[Order]):
    order_number: str
    entity_date: date
    due_date: date
    sold_to_customer_id: UUID
    factory_id: UUID
    details: list[OrderDetailInput]

    id: UUID | None = strawberry.UNSET
    published: bool = strawberry.UNSET
    creation_type: CreationType = strawberry.UNSET
    order_type: OrderType = strawberry.UNSET
    bill_to_customer_id: UUID | None = strawberry.UNSET
    shipping_terms: str | None = strawberry.UNSET
    freight_terms: str | None = strawberry.UNSET
    mark_number: str | None = strawberry.UNSET
    ship_date: date | None = strawberry.UNSET
    projected_ship_date: date | None = strawberry.UNSET
    fact_so_number: str | None = strawberry.UNSET
    quote_id: UUID | None = strawberry.UNSET
    inside_reps: list[OrderInsideRepInput] | None = strawberry.UNSET

    def to_orm_model(self) -> Order:
        inside_reps_val = self.optional_field(self.inside_reps)
        published = self.published if self.published != strawberry.UNSET else False
        creation_type = (
            self.creation_type
            if self.creation_type != strawberry.UNSET
            else CreationType.MANUAL
        )
        order_type = (
            self.order_type if self.order_type != strawberry.UNSET else OrderType.NORMAL
        )

        return Order(
            order_number=self.order_number,
            entity_date=self.entity_date,
            due_date=self.due_date,
            sold_to_customer_id=self.sold_to_customer_id,
            status=OrderStatus.OPEN,
            header_status=OrderHeaderStatus.OPEN,
            published=published,
            creation_type=creation_type,
            order_type=order_type,
            factory_id=self.factory_id,
            bill_to_customer_id=self.optional_field(self.bill_to_customer_id),
            shipping_terms=self.optional_field(self.shipping_terms),
            freight_terms=self.optional_field(self.freight_terms),
            mark_number=self.optional_field(self.mark_number),
            ship_date=self.optional_field(self.ship_date),
            projected_ship_date=self.optional_field(self.projected_ship_date),
            fact_so_number=self.optional_field(self.fact_so_number),
            quote_id=self.optional_field(self.quote_id),
            details=[detail.to_orm_model() for detail in self.details],
            inside_reps=(
                [rep.to_orm_model() for rep in inside_reps_val]
                if inside_reps_val
                else []
            ),
        )
