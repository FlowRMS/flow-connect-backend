"""Repository for PreOpportunityBalance entity with calculation logic."""

from collections.abc import Sequence
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.pre_opportunities.models.pre_opportunity_balance_model import (
    PreOpportunityBalance,
)
from app.graphql.pre_opportunities.models.pre_opportunity_detail_model import (
    PreOpportunityDetail,
)


class PreOpportunityBalanceRepository(BaseRepository[PreOpportunityBalance]):
    """Repository for PreOpportunityBalance entity with calculation logic."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, PreOpportunityBalance)

    def _sum_decimal(self, values: Sequence[Decimal]) -> Decimal:
        """Sum a sequence of decimal values safely."""
        return Decimal(sum(Decimal(v) for v in values))

    def calculate_balance_from_details(
        self,
        details: Sequence[PreOpportunityDetail],
        balance_id: UUID | None = None,
    ) -> PreOpportunityBalance:
        """
        Calculate balance totals from a list of details.

        Args:
            details: List of pre-opportunity detail items
            balance_id: Optional existing balance ID (for updates)

        Returns:
            PreOpportunityBalance instance with calculated values
        """
        quantity = self._sum_decimal([detail.quantity for detail in details])
        subtotal = self._sum_decimal([detail.subtotal for detail in details])
        discount = self._sum_decimal([detail.discount for detail in details])
        total = subtotal - discount

        # Calculate average discount rate
        discount_rate = (
            (discount / subtotal * Decimal("100")) if subtotal > 0 else Decimal("0.00")
        )

        balance = PreOpportunityBalance(
            subtotal=subtotal,
            total=total,
            discount=discount,
            discount_rate=discount_rate,
            quantity=quantity,
        )

        if balance_id:
            balance.id = balance_id

        return balance

    async def create_from_details(
        self, details: Sequence[PreOpportunityDetail]
    ) -> PreOpportunityBalance:
        """
        Create a new balance from details.

        Args:
            details: List of pre-opportunity detail items

        Returns:
            Created balance entity
        """
        balance = self.calculate_balance_from_details(details)
        return await self.create(balance)

    async def recalculate_balance(
        self, balance_id: UUID, details: Sequence[PreOpportunityDetail]
    ) -> PreOpportunityBalance:
        """
        Recalculate and update an existing balance.

        Args:
            balance_id: ID of the balance to update
            details: Current list of detail items

        Returns:
            Updated balance entity
        """
        updated_balance = self.calculate_balance_from_details(details, balance_id)
        return await self.update(updated_balance)
