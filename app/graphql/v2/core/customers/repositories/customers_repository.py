from typing import override

from commons.db.v6 import Customer, RbacResourceEnum
from commons.db.v6.crm.links.entity_type import EntityType
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.core.processors.executor import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService
from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy
from app.graphql.v2.rbac.strategies.created_by_filter import CreatedByFilterStrategy


class CustomersRepository(BaseRepository[Customer]):
    """Repository for Customers entity."""

    entity_type = EntityType.CUSTOMER

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        rbac_filter_service: RbacFilterService,
        processor_executor: ProcessorExecutor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Customer,
            rbac_filter_service,
            processor_executor,
        )

    @override
    def get_rbac_filter_strategy(self) -> RbacFilterStrategy | None:
        return CreatedByFilterStrategy(
            RbacResourceEnum.CUSTOMER,
            Customer,
        )

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

        result = await self.execute(stmt)
        return list(result.scalars().all())
