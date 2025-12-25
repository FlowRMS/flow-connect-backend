from typing import Any, override

from commons.db.v6 import Customer, RbacResourceEnum, User
from commons.db.v6.core.customers.customer_split_rate import CustomerSplitRate
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.user.rep_type import RepTypeEnum
from sqlalchemy import Select, String, func, literal, select
from sqlalchemy.dialects.postgresql import ARRAY, array
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.processors.executor import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.core.customers.processors.validate_split_rates_processor import (
    ValidateSplitRatesProcessor,
)
from app.graphql.v2.core.customers.strawberry.customer_landing_page_response import (
    CustomerLandingPageResponse,
)
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService
from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy
from app.graphql.v2.rbac.strategies.created_by_filter import CreatedByFilterStrategy


class CustomersRepository(BaseRepository[Customer]):
    entity_type = EntityType.CUSTOMER
    landing_model = CustomerLandingPageResponse
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.CUSTOMER

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        rbac_filter_service: RbacFilterService,
        processor_executor: ProcessorExecutor,
        validate_split_rates_processor: ValidateSplitRatesProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Customer,
            rbac_filter_service,
            processor_executor,
            processor_executor_classes=[validate_split_rates_processor],
        )

    @override
    def get_rbac_filter_strategy(self) -> RbacFilterStrategy | None:
        return CreatedByFilterStrategy(
            RbacResourceEnum.CUSTOMER,
            Customer,
        )

    def paginated_stmt(self) -> Select[Any]:
        inside_user = aliased(User)
        outside_user = aliased(User)
        empty_array = literal([]).cast(ARRAY(String))

        inside_subq = (
            select(
                CustomerSplitRate.customer_id,
                func.coalesce(func.array_agg(inside_user.full_name), empty_array).label(
                    "inside_reps"
                ),
            )
            .join(inside_user, inside_user.id == CustomerSplitRate.user_id)
            .where(CustomerSplitRate.rep_type == RepTypeEnum.INSIDE)
            .group_by(CustomerSplitRate.customer_id)
            .subquery()
        )

        outside_subq = (
            select(
                CustomerSplitRate.customer_id,
                func.coalesce(
                    func.array_agg(outside_user.full_name), empty_array
                ).label("outside_reps"),
            )
            .join(outside_user, outside_user.id == CustomerSplitRate.user_id)
            .where(CustomerSplitRate.rep_type == RepTypeEnum.OUTSIDE)
            .group_by(CustomerSplitRate.customer_id)
            .subquery()
        )

        return (
            select(
                Customer.id,
                Customer.created_at,
                User.full_name.label("created_by"),
                Customer.company_name,
                Customer.published,
                Customer.is_parent,
                Customer.contact_email,
                Customer.contact_number,
                func.coalesce(inside_subq.c.inside_reps, empty_array).label(
                    "inside_reps"
                ),
                func.coalesce(outside_subq.c.outside_reps, empty_array).label(
                    "outside_reps"
                ),
                array([Customer.created_by_id]).label("user_ids"),
            )
            .select_from(Customer)
            .options(lazyload("*"))
            .join(User, User.id == Customer.created_by_id)
            .outerjoin(inside_subq, inside_subq.c.customer_id == Customer.id)
            .outerjoin(outside_subq, outside_subq.c.customer_id == Customer.id)
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
