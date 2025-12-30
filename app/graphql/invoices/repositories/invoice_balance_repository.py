from collections.abc import Sequence
from decimal import Decimal
from typing import override
from uuid import UUID

from commons.db.v6.commission import InvoiceBalance, InvoiceDetail
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.common.repositories.base_balance_repository import (
    BaseBalanceRepository,
)


class InvoiceBalanceRepository(BaseBalanceRepository[InvoiceBalance, InvoiceDetail]):
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(context_wrapper, session, InvoiceBalance)

    @override
    def calculate_balance_from_details(
        self,
        details: Sequence[InvoiceDetail],
        balance_id: UUID | None = None,
    ) -> InvoiceBalance:
        quantity = self._sum_decimal([d.quantity for d in details])
        subtotal = self._sum_decimal([d.subtotal for d in details])
        discount = self._sum_decimal([d.discount for d in details])
        total = subtotal - discount
        commission = self._sum_decimal([d.commission for d in details])
        commission_discount = self._sum_decimal(
            [d.commission_discount for d in details]
        )

        discount_rate = self._calculate_rate(discount, subtotal)
        commission_rate = self._calculate_rate(commission, total)
        commission_discount_rate = self._calculate_rate(commission_discount, commission)

        balance = InvoiceBalance(
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
        balance.paid_balance = Decimal("0")

        if balance_id:
            balance.id = balance_id

        return balance
