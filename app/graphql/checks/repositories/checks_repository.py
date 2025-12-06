"""Repository for Check entity with specific database operations."""

from uuid import UUID

from commons.db.models import Check
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.links.models.entity_type import EntityType
from app.graphql.links.models.link_relation_model import LinkRelation


class ChecksRepository(BaseRepository[Check]):
    """Repository for Checks entity."""

    entity_type = EntityType.CHECK

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Check)

    async def search_by_check_number(
        self, search_term: str, limit: int = 20
    ) -> list[Check]:
        """
        Search checks by check number using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against check number
            limit: Maximum number of checks to return (default: 20)

        Returns:
            List of Check objects matching the search criteria
        """
        stmt = (
            select(Check)
            .options(lazyload("*"))
            .where(Check.check_number.ilike(f"%{search_term}%"))
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_job_id(self, job_id: UUID) -> list[Check]:
        """
        Find all checks linked to the given job ID.

        Args:
            job_id: The job ID to find checks for

        Returns:
            List of Check objects linked to the given job ID
        """
        stmt = (
            select(Check)
            .options(lazyload("*"))
            .join(
                LinkRelation,
                or_(
                    (
                        (LinkRelation.source_entity_type == EntityType.CHECK)
                        & (LinkRelation.target_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_id == job_id)
                        & (LinkRelation.source_entity_id == Check.id)
                    ),
                    (
                        (LinkRelation.source_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_type == EntityType.CHECK)
                        & (LinkRelation.source_entity_id == job_id)
                        & (LinkRelation.target_entity_id == Check.id)
                    ),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
