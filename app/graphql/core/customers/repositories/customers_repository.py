from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.core.customers.models import CustomerV2
from app.graphql.links.models.entity_type import EntityType


class CustomersRepository(BaseRepository[CustomerV2]):
    """Repository for Customers entity."""

    entity_type = EntityType.CUSTOMER

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, CustomerV2)

    async def search_by_company_name(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[CustomerV2]:
        """
        Search customers by company name using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against company name
            published: Filter by published status (default: True)
            limit: Maximum number of customers to return (default: 20)

        Returns:
            List of CustomerV2 objects matching the search criteria
        """
        stmt = (
            select(CustomerV2)
            .where(CustomerV2.company_name.ilike(f"%{search_term}%"))
            .limit(limit)
        )

        if published is not None:
            stmt = stmt.where(CustomerV2.published == published)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
