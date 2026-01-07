from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission.orders import OrderDetail

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.orders.strawberry.order_inside_rep_input import OrderInsideRepInput
from app.graphql.orders.strawberry.order_split_rate_input import OrderSplitRateInput


@strawberry.input
class OrderDetailInput(BaseInputGQL[OrderDetail]):
    item_number: int
    quantity: Decimal
    unit_price: Decimal
    end_user_id: UUID
    id: UUID | None = None
    uom_id: UUID | None = None
    division_factor: Decimal | None = None
    product_id: UUID | None = None
    product_name_adhoc: str | None = None
    product_description_adhoc: str | None = None
    lead_time: str | None = None
    note: str | None = None
    discount_rate: Decimal = Decimal("0")
    commission_rate: Decimal = Decimal("0")
    commission_discount_rate: Decimal = Decimal("0")
    freight_charge: Decimal = Decimal("0")
    outside_split_rates: list[OrderSplitRateInput] | None = None
    inside_split_rates: list[OrderInsideRepInput] | None = None

    def to_orm_model(self) -> OrderDetail:
        subtotal = self.quantity * self.unit_price
        discount = subtotal * (self.discount_rate / Decimal("100"))
        total = subtotal - discount
        commission = total * (self.commission_rate / Decimal("100"))
        commission_discount = commission * (
            self.commission_discount_rate / Decimal("100")
        )
        total_line_commission = commission - commission_discount

        detail = OrderDetail(
            item_number=self.item_number,
            quantity=self.quantity,
            unit_price=self.unit_price,
            subtotal=subtotal,
            discount_rate=self.discount_rate,
            discount=discount,
            total=total,
            commission_rate=self.commission_rate,
            commission=commission,
            commission_discount_rate=self.commission_discount_rate,
            commission_discount=commission_discount,
            total_line_commission=total_line_commission,
            product_id=self.product_id,
            product_name_adhoc=self.product_name_adhoc,
            product_description_adhoc=self.product_description_adhoc,
            end_user_id=self.end_user_id,
            uom_id=self.uom_id,
            division_factor=self.division_factor,
            lead_time=self.lead_time,
            note=self.note,
            freight_charge=self.freight_charge,
            outside_split_rates=(
                [sr.to_orm_model() for sr in self.outside_split_rates]
                if self.outside_split_rates
                else []
            ),
            inside_split_rates=(
                [ir.to_orm_model() for ir in self.inside_split_rates]
                if self.inside_split_rates
                else []
            ),
        )
        if self.id:
            detail.id = self.id
        return detail
