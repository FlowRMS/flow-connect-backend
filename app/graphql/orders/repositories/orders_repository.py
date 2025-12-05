"""Repository for Order entity with specific database operations."""

from uuid import UUID

from commons.db.models import Order
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.links.models.entity_type import EntityType
from app.graphql.links.models.link_relation_model import LinkRelation


class OrdersRepository(BaseRepository[Order]):
    """Repository for Orders entity."""

    entity_type = EntityType.ORDER

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Order)

    async def search_by_order_number(
        self, search_term: str, limit: int = 20
    ) -> list[Order]:
        """
        Search orders by order number using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against order number
            limit: Maximum number of orders to return (default: 20)

        Returns:
            List of Order objects matching the search criteria
        """
        stmt = (
            select(Order)
            .options(lazyload("*"))
            .where(Order.order_number.ilike(f"%{search_term}%"))
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_job_id(self, job_id: UUID) -> list[Order]:
        """
        Find all orders linked to the given job ID.

        Args:
            job_id: The job ID to find orders for

        Returns:
            List of Order objects linked to the given job ID
        """
        stmt = select(Order).join(
            LinkRelation,
            or_(
                (
                    (LinkRelation.source_entity_type == EntityType.ORDER)
                    & (LinkRelation.target_entity_type == EntityType.JOB)
                    & (LinkRelation.target_entity_id == job_id)
                    & (LinkRelation.source_entity_id == Order.id)
                ),
                (
                    (LinkRelation.source_entity_type == EntityType.JOB)
                    & (LinkRelation.target_entity_type == EntityType.ORDER)
                    & (LinkRelation.source_entity_id == job_id)
                    & (LinkRelation.target_entity_id == Order.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
