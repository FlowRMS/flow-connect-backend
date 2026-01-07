from abc import ABC, abstractmethod
from collections.abc import Sequence
from decimal import Decimal
from typing import Generic, TypeVar
from uuid import UUID

from commons.db.v6 import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository

TBalance = TypeVar("TBalance", bound=BaseModel)
TDetail = TypeVar("TDetail", bound=BaseModel)


class BaseBalanceRepository(BaseRepository[TBalance], ABC, Generic[TBalance, TDetail]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        model_class: type[TBalance],
    ) -> None:
        super().__init__(session, context_wrapper, model_class)

    def _sum_decimal(self, values: Sequence[Decimal]) -> Decimal:
        return Decimal(sum(Decimal(v) for v in values))

    def _calculate_rate(self, part: Decimal, whole: Decimal) -> Decimal:
        return (part / whole * Decimal("100")) if whole > 0 else Decimal("0")

    @abstractmethod
    def calculate_balance_from_details(
        self,
        details: Sequence[TDetail],
        balance_id: UUID | None = None,
    ) -> TBalance:
        raise NotImplementedError

    async def create_from_details(self, details: Sequence[TDetail]) -> TBalance:
        balance = self.calculate_balance_from_details(details)
        return await self.create(balance)

    async def recalculate_balance(
        self, balance_id: UUID, details: Sequence[TDetail]
    ) -> TBalance:
        updated_balance = self.calculate_balance_from_details(details, balance_id)
        return await self.update(updated_balance)
