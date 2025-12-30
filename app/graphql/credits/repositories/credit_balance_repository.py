from collections.abc import Sequence
from typing import override
from uuid import UUID

from commons.db.v6.commission import CreditBalance, CreditDetail
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.common.repositories.base_balance_repository import (
    BaseBalanceRepository,
)


class CreditBalanceRepository(BaseBalanceRepository[CreditBalance, CreditDetail]):
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(context_wrapper, session, CreditBalance)

    @override
    def calculate_balance_from_details(
        self,
        details: Sequence[CreditDetail],
        balance_id: UUID | None = None,
    ) -> CreditBalance:
        quantity = self._sum_decimal([d.quantity for d in details])
        subtotal = self._sum_decimal([d.subtotal for d in details])
        total = subtotal
        commission = self._sum_decimal([d.commission for d in details])

        balance = CreditBalance(
            quantity=quantity,
            subtotal=subtotal,
            total=total,
            commission=commission,
        )

        if balance_id:
            balance.id = balance_id

        return balance
