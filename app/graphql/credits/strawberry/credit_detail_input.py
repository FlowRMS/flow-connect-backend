from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.commission import CreditDetail

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class CreditDetailInput(BaseInputGQL[CreditDetail]):
    item_number: int
    quantity: Decimal
    unit_price: Decimal
    commission_rate: Decimal
    order_detail_id: UUID
    id: UUID | None = None

    def to_orm_model(self) -> CreditDetail:
        subtotal = self.quantity * self.unit_price
        total = subtotal
        commission = total * (self.commission_rate / Decimal("100"))

        detail = CreditDetail(
            order_detail_id=self.order_detail_id,
            item_number=self.item_number,
            quantity=self.quantity,
            unit_price=self.unit_price,
            subtotal=subtotal,
            total=total,
            commission_rate=self.commission_rate,
            commission=commission,
        )
        if self.id:
            detail.id = self.id
        return detail
