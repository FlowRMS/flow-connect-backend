from collections.abc import Sequence
from typing import override
from uuid import UUID

from commons.db.v6.commission.orders import OrderBalance, OrderDetail
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.common.repositories.base_balance_repository import (
    BaseBalanceRepository,
)


class OrderBalanceRepository(BaseBalanceRepository[OrderBalance, OrderDetail]):
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(context_wrapper, session, OrderBalance)

    @override
    def calculate_balance_from_details(
        self,
        details: Sequence[OrderDetail],
        balance_id: UUID | None = None,
    ) -> OrderBalance:
        quantity = self._sum_decimal([d.quantity for d in details])
        subtotal = self._sum_decimal([d.subtotal for d in details])
        discount = self._sum_decimal([d.discount for d in details])
        total = subtotal - discount
        commission = self._sum_decimal([d.commission for d in details])
        commission_discount = self._sum_decimal(
            [d.commission_discount for d in details]
        )

        shipping_balance = self._sum_decimal([d.shipping_balance for d in details])
        cancelled_balance = self._sum_decimal([d.cancelled_balance for d in details])
        freight_charge_balance = self._sum_decimal([d.freight_charge for d in details])

        discount_rate = self._calculate_rate(discount, subtotal)
        commission_rate = self._calculate_rate(commission, total)
        commission_discount_rate = self._calculate_rate(commission_discount, commission)

        balance = OrderBalance(
            quantity=quantity,
            subtotal=subtotal,
            total=total,
            commission=commission,
            discount=discount,
            discount_rate=discount_rate,
            commission_rate=commission_rate,
            commission_discount=commission_discount,
            commission_discount_rate=commission_discount_rate,
        )
        balance.shipping_balance = shipping_balance
        balance.cancelled_balance = cancelled_balance
        balance.freight_charge_balance = freight_charge_balance

        if balance_id:
            balance.id = balance_id

        return balance
