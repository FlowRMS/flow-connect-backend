from typing import override

from commons.db.v6 import RbacResourceEnum
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.core.processors.executor import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.links.models.entity_type import EntityType
from app.graphql.v2.core.customers.models import CustomerV2
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService
from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy
from app.graphql.v2.rbac.strategies.created_by_filter import CreatedByFilterStrategy


class CustomersRepository(BaseRepository[CustomerV2]):
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
            CustomerV2,
            rbac_filter_service,
            processor_executor,
        )

    @override
    def get_rbac_filter_strategy(self) -> RbacFilterStrategy | None:
        return CreatedByFilterStrategy(
            RbacResourceEnum.CUSTOMER,
            CustomerV2,
        )

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

        result = await self.execute(stmt)
        return list(result.scalars().all())
