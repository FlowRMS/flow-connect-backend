"""Repository for PreOpportunity entity with specific database operations."""

from typing import Any
from uuid import UUID

from commons.db.models import User
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.pre_opportunities.models.pre_opportunity_balance_model import (
    PreOpportunityBalance,
)
from app.graphql.pre_opportunities.models.pre_opportunity_model import PreOpportunity
from app.graphql.pre_opportunities.repositories.pre_opportunity_balance_repository import (
    PreOpportunityBalanceRepository,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_landing_page_response import (
    PreOpportunityLandingPageResponse,
)


class PreOpportunitiesRepository(BaseRepository[PreOpportunity]):
    """Repository for PreOpportunity entity."""

    landing_model = PreOpportunityLandingPageResponse

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        balance_repository: PreOpportunityBalanceRepository,
    ) -> None:
        super().__init__(session, context_wrapper, PreOpportunity)
        self.balance_repository = balance_repository

    def paginated_stmt(self) -> Select[Any]:
        """
        Build paginated query for pre-opportunities landing page.

        Returns:
            SQLAlchemy select statement with columns for landing page
        """
        return (
            select(
                PreOpportunity.id,
                PreOpportunity.created_at,
                User.full_name.label("created_by"),
                PreOpportunity.entity_number,
                PreOpportunity.status,
                PreOpportunity.entity_date,
                PreOpportunity.exp_date,
                PreOpportunityBalance.total.label("total"),
                PreOpportunity.tags,
            )
            .select_from(PreOpportunity)
            .options(lazyload("*"))
            .join(User, User.id == PreOpportunity.created_by)
            .join(
                PreOpportunityBalance,
                PreOpportunityBalance.id == PreOpportunity.balance_id,
            )
        )

    async def create_with_balance(
        self, pre_opportunity: PreOpportunity
    ) -> PreOpportunity:
        """
        Create a new pre-opportunity with balance calculation.

        Args:
            pre_opportunity: The pre-opportunity entity to create

        Returns:
            Created pre-opportunity with balance
        """
        # Create balance from details
        balance = await self.balance_repository.create_from_details(
            pre_opportunity.details
        )
        pre_opportunity.balance_id = balance.id

        # Create the pre-opportunity
        return await self.create(pre_opportunity)

    async def update_with_balance(
        self, pre_opportunity: PreOpportunity
    ) -> PreOpportunity:
        """
        Update a pre-opportunity and recalculate its balance.

        Args:
            pre_opportunity: The pre-opportunity entity to update

        Returns:
            Updated pre-opportunity with recalculated balance
        """
        updated = await self.update(pre_opportunity)
        _ = await self.balance_repository.recalculate_balance(
            updated.balance_id, updated.details
        )
        await self.session.refresh(updated)
        return updated

    async def get_by_job_id(self, job_id: UUID) -> list[PreOpportunity]:
        """Get all pre-opportunities for a specific job."""
        stmt = select(PreOpportunity).where(PreOpportunity.job_id == job_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_customer_id(self, customer_id: UUID) -> list[PreOpportunity]:
        """Get all pre-opportunities for a specific customer."""
        stmt = select(PreOpportunity).where(
            PreOpportunity.sold_to_customer_id == customer_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
