from typing import Any, override
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.commission.orders import (
    Order,
    OrderBalance,
    OrderDetail,
    OrderInsideRep,
    OrderSplitRate,
)
from commons.db.v6.core import Customer, Factory
from commons.db.v6.crm.jobs.jobs_model import Job
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from sqlalchemy import Select, func, literal, or_, select
from sqlalchemy.dialects.postgresql import ARRAY, array
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.exceptions import NotFoundError
from app.core.processors import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.orders.repositories.order_balance_repository import (
    OrderBalanceRepository,
)
from app.graphql.orders.strategies.order_owner_filter import OrderOwnerFilterStrategy
from app.graphql.orders.strawberry.order_landing_page_response import (
    OrderLandingPageResponse,
)
from app.graphql.quotes.processors.validate_rep_split_processor import (
    ValidateRepSplitProcessor,
)
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService
from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy


class OrdersRepository(BaseRepository[Order]):
    entity_type = EntityType.ORDER
    landing_model = OrderLandingPageResponse
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.ORDER

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        balance_repository: OrderBalanceRepository,
        rbac_filter_service: RbacFilterService,
        processor_executor: ProcessorExecutor,
        validate_rep_split_processor: ValidateRepSplitProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Order,
            rbac_filter_service,
            processor_executor,
            processor_executor_classes=[validate_rep_split_processor],
        )
        self.balance_repository = balance_repository

    @override
    def get_rbac_filter_strategy(self) -> RbacFilterStrategy | None:
        return OrderOwnerFilterStrategy(RbacResourceEnum.ORDER)

    def paginated_stmt(self) -> Select[Any]:
        empty_array = literal([]).cast(ARRAY(PG_UUID))

        inside_rep_user_ids_subq = (
            select(
                OrderDetail.order_id,
                func.array_agg(OrderInsideRep.user_id).label("inside_rep_user_ids"),
            )
            .join(OrderInsideRep, OrderInsideRep.order_detail_id == OrderDetail.id)
            .group_by(OrderDetail.order_id)
            .subquery()
        )

        split_rate_user_ids_subq = (
            select(
                OrderDetail.order_id,
                func.array_agg(OrderSplitRate.user_id.distinct()).label(
                    "split_rate_user_ids"
                ),
            )
            .join(OrderSplitRate, OrderSplitRate.order_detail_id == OrderDetail.id)
            .group_by(OrderDetail.order_id)
            .subquery()
        )

        user_ids_expr = func.array_cat(
            func.array_cat(
                array([Order.created_by_id]),
                func.coalesce(
                    inside_rep_user_ids_subq.c.inside_rep_user_ids, empty_array
                ),
            ),
            func.coalesce(split_rate_user_ids_subq.c.split_rate_user_ids, empty_array),
        ).label("user_ids")

        return (
            select(
                Order.id,
                Order.created_at,
                User.full_name.label("created_by"),
                Order.order_number,
                Order.status,
                Order.header_status,
                Order.order_type,
                Order.entity_date,
                Order.due_date,
                OrderBalance.total.label("total"),
                OrderBalance.commission.label("commission"),
                Order.published,
                Factory.title.label("factory_name"),
                Job.job_name.label("job_name"),
                Customer.company_name.label("sold_to_customer_name"),
                user_ids_expr,
            )
            .select_from(Order)
            .options(lazyload("*"))
            .join(User, User.id == Order.created_by_id)
            .join(OrderBalance, OrderBalance.id == Order.balance_id)
            .join(Factory, Factory.id == Order.factory_id)
            .join(Customer, Customer.id == Order.sold_to_customer_id)
            .outerjoin(Job, Job.id == Order.job_id)
            .outerjoin(
                inside_rep_user_ids_subq,
                inside_rep_user_ids_subq.c.order_id == Order.id,
            )
            .outerjoin(
                split_rate_user_ids_subq,
                split_rate_user_ids_subq.c.order_id == Order.id,
            )
        )

    async def find_order_by_id(self, order_id: UUID) -> Order:
        order = await self.get_by_id(
            order_id,
            options=[
                joinedload(Order.details),
                joinedload(Order.details).joinedload(OrderDetail.product),
                joinedload(Order.details).joinedload(OrderDetail.outside_split_rates),
                joinedload(Order.details).joinedload(OrderDetail.inside_split_rates),
                joinedload(Order.details).joinedload(OrderDetail.uom),
                joinedload(Order.balance),
                joinedload(Order.sold_to_customer),
                joinedload(Order.bill_to_customer),
                joinedload(Order.created_by),
                joinedload(Order.job),
                joinedload(Order.factory),
                lazyload("*"),
            ],
        )
        if not order:
            raise NotFoundError(str(order_id))
        return order

    async def create_with_balance(self, order: Order) -> Order:
        balance = await self.balance_repository.create_from_details(order.details)
        order.balance_id = balance.id
        _ = await self.create(order)
        return await self.find_order_by_id(order.id)

    async def update_with_balance(self, order: Order) -> Order:
        updated = await self.update(order)
        _ = await self.balance_repository.recalculate_balance(
            updated.balance_id, updated.details
        )
        await self.session.flush()
        return await self.find_order_by_id(updated.id)

    async def order_number_exists(self, order_number: str) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(Order)
            .options(lazyload("*"))
            .where(Order.order_number == order_number)
        )
        return result.scalar_one() > 0

    async def search_by_order_number(
        self, search_term: str, limit: int = 20
    ) -> list[Order]:
        stmt = (
            select(Order)
            .options(lazyload("*"))
            .where(Order.order_number.ilike(f"%{search_term}%"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_job_id(self, job_id: UUID) -> list[Order]:
        stmt = (
            select(Order)
            .options(lazyload("*"))
            .join(
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
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
