from commons.db.models import Customer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class CustomersRepository(BaseRepository[Customer]):
    """Repository for Customers entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Customer)

    async def search_by_company_name(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[Customer]:
        """
        Search customers by company name using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against company name
            published: Filter by published status (default: True)
            limit: Maximum number of customers to return (default: 20)

        Returns:
            List of Customer objects matching the search criteria
        """
        stmt = (
            select(Customer)
            .where(Customer.company_name.ilike(f"%{search_term}%"))
            .limit(limit)
        )

        if published is not None:
            stmt = stmt.where(Customer.published == published)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
