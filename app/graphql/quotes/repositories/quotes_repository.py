"""Repository for Quote entity with specific database operations."""

from uuid import UUID

from commons.db.models import Quote
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.links.models.entity_type import EntityType
from app.graphql.links.models.link_relation_model import LinkRelation


class QuotesRepository(BaseRepository[Quote]):
    """Repository for Quotes entity."""

    entity_type = EntityType.QUOTE

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Quote)

    async def search_by_quote_number(
        self, search_term: str, limit: int = 20
    ) -> list[Quote]:
        """
        Search quotes by quote number using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against quote number
            limit: Maximum number of quotes to return (default: 20)

        Returns:
            List of Quote objects matching the search criteria
        """
        stmt = (
            select(Quote)
            .options(lazyload("*"))
            .where(Quote.quote_number.ilike(f"%{search_term}%"))
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_job_id(self, job_id: UUID) -> list[Quote]:
        """
        Find all quotes linked to the given job ID.

        Args:
            job_id: The job ID to find quotes for

        Returns:
            List of Quote objects linked to the given job ID
        """
        stmt = (
            select(Quote)
            .options(lazyload("*"))
            .join(
                LinkRelation,
                or_(
                    (
                        (LinkRelation.source_entity_type == EntityType.QUOTE)
                        & (LinkRelation.target_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_id == job_id)
                        & (LinkRelation.source_entity_id == Quote.id)
                    ),
                    (
                        (LinkRelation.source_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_type == EntityType.QUOTE)
                        & (LinkRelation.source_entity_id == job_id)
                        & (LinkRelation.target_entity_id == Quote.id)
                    ),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
