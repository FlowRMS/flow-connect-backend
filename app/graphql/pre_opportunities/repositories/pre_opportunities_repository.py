"""Repository for PreOpportunity entity with specific database operations."""

from typing import Any
from uuid import UUID

from commons.db.models import User
from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.links.models.entity_type import EntityType
from app.graphql.links.models.link_relation_model import LinkRelation
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
            .join(User, User.id == PreOpportunity.created_by_id)
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

    async def entity_number_exists(self, entity_number: str) -> bool:
        """
        Check if a pre-opportunity with the given entity number already exists.

        Args:
            entity_number: The entity number to check

        Returns:
            True if a pre-opportunity with this entity number exists, False otherwise
        """
        result = await self.session.execute(
            select(func.count())
            .select_from(PreOpportunity)
            .where(PreOpportunity.entity_number == entity_number)
        )
        return result.scalar_one() > 0

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

    async def search_by_entity_number(
        self, search_term: str, limit: int = 20
    ) -> list[PreOpportunity]:
        """
        Search pre-opportunities by entity number using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against entity number
            limit: Maximum number of pre-opportunities to return (default: 20)

        Returns:
            List of PreOpportunity objects matching the search criteria
        """
        stmt = (
            select(PreOpportunity)
            .where(PreOpportunity.entity_number.ilike(f"%{search_term}%"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[PreOpportunity]:
        """
        Find all pre-opportunities linked to a specific entity via link relations.

        Args:
            entity_type: The type of entity to find pre-opportunities for
            entity_id: The ID of the entity

        Returns:
            List of PreOpportunity objects linked to the entity
        """
        stmt = select(PreOpportunity).join(
            LinkRelation,
            or_(
                # PreOpportunity as source, entity as target
                (
                    (LinkRelation.source_entity_type == EntityType.PRE_OPPORTUNITY)
                    & (LinkRelation.target_entity_type == entity_type)
                    & (LinkRelation.target_entity_id == entity_id)
                    & (LinkRelation.source_entity_id == PreOpportunity.id)
                ),
                # Entity as source, PreOpportunity as target
                (
                    (LinkRelation.source_entity_type == entity_type)
                    & (LinkRelation.target_entity_type == EntityType.PRE_OPPORTUNITY)
                    & (LinkRelation.source_entity_id == entity_id)
                    & (LinkRelation.target_entity_id == PreOpportunity.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
