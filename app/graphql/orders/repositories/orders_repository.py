from typing import Any, override
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.commission.orders import (
    Order,
    OrderBalance,
    OrderDetail,
)
from commons.db.v6.core import Customer, Factory
from commons.db.v6.crm.jobs.jobs_model import Job
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.exceptions import NotFoundError
from app.core.processors import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.orders.processors.default_rep_split_processor import (
    OrderDefaultRepSplitProcessor,
)
from app.graphql.orders.processors.set_shipping_balance_processor import (
    SetShippingBalanceProcessor,
)
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
        set_shipping_balance_processor: SetShippingBalanceProcessor,
        order_default_rep_split_processor: OrderDefaultRepSplitProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Order,
            rbac_filter_service,
            processor_executor,
            processor_executor_classes=[
                order_default_rep_split_processor,
                validate_rep_split_processor,
                set_shipping_balance_processor,
            ],
        )
        self.balance_repository = balance_repository

    @override
    def get_rbac_filter_strategy(self) -> RbacFilterStrategy | None:
        return OrderOwnerFilterStrategy(RbacResourceEnum.ORDER)

    def paginated_stmt(self) -> Select[Any]:
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
                Order.user_ids,
            )
            .select_from(Order)
            .options(lazyload("*"))
            .join(User, User.id == Order.created_by_id)
            .join(OrderBalance, OrderBalance.id == Order.balance_id)
            .join(Factory, Factory.id == Order.factory_id)
            .join(Customer, Customer.id == Order.sold_to_customer_id)
            .outerjoin(Job, Job.id == Order.job_id)
        )

    @override
    def compute_user_ids(self, order: Order) -> list[UUID]:
        user_ids: set[UUID] = {self.auth_info.flow_user_id}
        for detail in order.details:
            for split_rate in detail.outside_split_rates:
                user_ids.add(split_rate.user_id)
            for inside_rep in detail.inside_split_rates:
                user_ids.add(inside_rep.user_id)
        return list(user_ids)

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

    async def order_number_exists(
        self, order_number: str, customer_id: UUID | None
    ) -> bool:
        stmt = (
            select(func.count())
            .select_from(Order)
            .options(lazyload("*"))
            .where(Order.order_number == order_number)
        )
        if customer_id:
            stmt = stmt.where(Order.sold_to_customer_id == customer_id)

        result = await self.session.execute(stmt)
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

    async def find_by_factory_id(
        self, factory_id: UUID, limit: int = 25
    ) -> list[Order]:
        stmt = (
            select(Order)
            .options(lazyload("*"))
            .where(Order.factory_id == factory_id)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
