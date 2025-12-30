from collections.abc import Sequence
from decimal import Decimal
from uuid import UUID

from commons.db.v6.crm.quotes import QuoteBalance, QuoteDetail
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class QuoteBalanceRepository(BaseRepository[QuoteBalance]):
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, QuoteBalance)

    def _sum_decimal(self, values: Sequence[Decimal]) -> Decimal:
        return Decimal(sum(Decimal(v) for v in values))

    def calculate_balance_from_details(
        self,
        details: Sequence[QuoteDetail],
        balance_id: UUID | None = None,
    ) -> QuoteBalance:
        quantity = self._sum_decimal([detail.quantity for detail in details])
        subtotal = self._sum_decimal([detail.subtotal for detail in details])
        discount = self._sum_decimal([detail.discount for detail in details])
        total = subtotal - discount
        commission = self._sum_decimal([detail.commission for detail in details])
        commission_discount = self._sum_decimal(
            [detail.commission_discount for detail in details]
        )

        discount_rate = (
            (discount / subtotal * Decimal("100")) if subtotal > 0 else Decimal("0")
        )
        commission_rate = (
            (commission / total * Decimal("100")) if total > 0 else Decimal("0")
        )
        commission_discount_rate = (
            (commission_discount / commission * Decimal("100"))
            if commission > 0
            else Decimal("0")
        )

        balance = QuoteBalance(
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

        if balance_id:
            balance.id = balance_id

        return balance

    async def create_from_details(self, details: Sequence[QuoteDetail]) -> QuoteBalance:
        balance = self.calculate_balance_from_details(details)
        return await self.create(balance)

    async def recalculate_balance(
        self, balance_id: UUID, details: Sequence[QuoteDetail]
    ) -> QuoteBalance:
        updated_balance = self.calculate_balance_from_details(details, balance_id)
        return await self.update(updated_balance)
