from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission import CreditDetail

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.credits.strawberry.credit_split_rate_input import CreditSplitRateInput


@strawberry.input
class CreditDetailInput(BaseInputGQL[CreditDetail]):
    item_number: int
    quantity: Decimal
    unit_price: Decimal
    commission_rate: Decimal
    order_detail_id: UUID
    id: UUID | None = None
    outside_split_rates: list[CreditSplitRateInput] | None = None

    def to_orm_model(self) -> CreditDetail:
        quantity = self.quantity if self.quantity is not None else Decimal("0")
        unit_price = self.unit_price if self.unit_price is not None else Decimal("0")

        subtotal = quantity * unit_price
        total = subtotal
        commission = total * (self.commission_rate / Decimal("100"))

        detail = CreditDetail(
            order_detail_id=self.order_detail_id,
            item_number=self.item_number,
            quantity=quantity,
            unit_price=unit_price,
            subtotal=subtotal,
            total=total,
            commission_rate=self.commission_rate,
            commission=commission,
            outside_split_rates=(
                [sr.to_orm_model() for sr in self.outside_split_rates]
                if self.outside_split_rates
                else []
            ),
        )
        if self.id:
            detail.id = self.id
        return detail
