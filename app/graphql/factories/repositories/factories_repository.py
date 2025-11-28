from commons.db.models.core.factory import Factory
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class FactoriesRepository(BaseRepository[Factory]):
    """Repository for Factories entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Factory)

    async def search_by_title(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[Factory]:
        """
        Search factories by title using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against title
            published: Filter by published status (default: True)
            limit: Maximum number of factories to return (default: 20)

        Returns:
            List of Factory objects matching the search criteria
        """
        stmt = (
            select(Factory).where(Factory.title.ilike(f"%{search_term}%")).limit(limit)
        )

        if published is not None:
            stmt = stmt.where(Factory.published == published)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
