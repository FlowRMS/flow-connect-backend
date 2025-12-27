from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.commission.orders import OrderBalance

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class OrderBalanceResponse(DTOMixin[OrderBalance]):
    id: UUID
    quantity: Decimal
    subtotal: Decimal
    total: Decimal
    commission: Decimal
    discount: Decimal
    discount_rate: Decimal
    commission_rate: Decimal
    commission_discount: Decimal
    commission_discount_rate: Decimal
    shipping_balance: Decimal
    cancelled_balance: Decimal
    freight_charge_balance: Decimal

    @classmethod
    def from_orm_model(cls, model: OrderBalance) -> Self:
        return cls(
            id=model.id,
            quantity=model.quantity,
            subtotal=model.subtotal,
            total=model.total,
            commission=model.commission,
            discount=model.discount,
            discount_rate=model.discount_rate,
            commission_rate=model.commission_rate,
            commission_discount=model.commission_discount,
            commission_discount_rate=model.commission_discount_rate,
            shipping_balance=model.shipping_balance,
            cancelled_balance=model.cancelled_balance,
            freight_charge_balance=model.freight_charge_balance,
        )
