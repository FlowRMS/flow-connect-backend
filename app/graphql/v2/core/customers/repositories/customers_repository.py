from typing import Any, override
from uuid import UUID

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

    async def company_name_exists(self, company_name: str) -> bool:
        stmt = select(func.count()).where(Customer.company_name == company_name)
        result = await self.session.execute(stmt)
        count = result.scalar_one()
        return count > 0

    async def get_existing_company_names(self, company_names: list[str]) -> set[str]:
        if not company_names:
            return set()
        stmt = select(Customer.company_name).where(
            Customer.company_name.in_(company_names)
        )
        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    def paginated_stmt(self) -> Select[Any]:
        inside_user = aliased(User)
        outside_user = aliased(User)
        buying_group = aliased(Customer)
        parent = aliased(Customer)
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
                buying_group.company_name.label("buying_group"),
                parent.company_name.label("parent"),
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
            .outerjoin(buying_group, buying_group.id == Customer.buying_group_id)
            .outerjoin(parent, parent.id == Customer.parent_id)
            .join(User, User.id == Customer.created_by_id)
            .outerjoin(inside_subq, inside_subq.c.customer_id == Customer.id)
            .outerjoin(outside_subq, outside_subq.c.customer_id == Customer.id)
        )

    async def search_by_company_name(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[Customer]:
        stmt = (
            select(Customer)
            .where(Customer.company_name.ilike(f"%{search_term}%"))
            .limit(limit)
        )

        if published is not None:
            stmt = stmt.where(Customer.published == published)

        result = await self.execute(stmt)
        return list(result.scalars().all())

    async def get_buying_group_members(self, buying_group_id: UUID) -> list[Customer]:
        stmt = select(Customer).where(Customer.buying_group_id == buying_group_id)
        result = await self.execute(stmt)
        return list(result.scalars().all())

    async def get_children(self, parent_id: UUID) -> list[Customer]:
        stmt = select(Customer).where(Customer.parent_id == parent_id)
        result = await self.execute(stmt)
        return list(result.scalars().all())
