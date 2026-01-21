from typing import Any, override
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.core import Customer, Factory, Product
from commons.db.v6.core.products import ProductCategory
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from commons.db.v6.crm.quotes import (
    Quote,
    QuoteBalance,
    QuoteDetail,
    QuoteSplitRate,
)
from sqlalchemy import Select, String, cast, func, or_, select, text, update
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, array_agg
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, joinedload, lazyload
from sqlalchemy.sql.selectable import Subquery

from app.core.context_wrapper import ContextWrapper
from app.core.exceptions import NotFoundError
from app.core.processors import ProcessorExecutor, ValidateCommissionRateProcessor
from app.graphql.base_repository import BaseRepository
from app.graphql.quotes.processors.default_rep_split_processor import (
    DefaultRepSplitProcessor,
)
from app.graphql.quotes.processors.validate_rep_split_processor import (
    ValidateRepSplitProcessor,
)
from app.graphql.quotes.repositories.quote_balance_repository import (
    QuoteBalanceRepository,
)
from app.graphql.quotes.strategies.quote_owner_filter import QuoteOwnerFilterStrategy
from app.graphql.quotes.strawberry.quote_landing_page_response import (
    QuoteLandingPageResponse,
)
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService
from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy


class QuotesRepository(BaseRepository[Quote]):
    entity_type = EntityType.QUOTE
    landing_model = QuoteLandingPageResponse
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.QUOTE

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        balance_repository: QuoteBalanceRepository,
        rbac_filter_service: RbacFilterService,
        processor_executor: ProcessorExecutor,
        default_rep_split_processor: DefaultRepSplitProcessor,
        validate_rep_split_processor: ValidateRepSplitProcessor,
        validate_commission_rate_processor: ValidateCommissionRateProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Quote,
            rbac_filter_service,
            processor_executor,
            processor_executor_classes=[
                default_rep_split_processor,
                validate_rep_split_processor,
                validate_commission_rate_processor,
            ],
        )
        self.balance_repository = balance_repository

    @override
    def get_rbac_filter_strategy(self) -> RbacFilterStrategy | None:
        return QuoteOwnerFilterStrategy(RbacResourceEnum.QUOTE)

    def _sales_reps_subquery(self) -> Subquery[Any]:
        sales_rep = aliased(User)
        per_user_agg = (
            select(
                QuoteDetail.quote_id,
                sales_rep.full_name.label("full_name"),
                func.sum(QuoteDetail.total).label("total"),
                func.avg(QuoteSplitRate.split_rate).label("avg_split_rate"),
            )
            .select_from(QuoteDetail)
            .join(QuoteSplitRate, QuoteSplitRate.quote_detail_id == QuoteDetail.id)
            .join(sales_rep, sales_rep.id == QuoteSplitRate.user_id)
            .group_by(QuoteDetail.quote_id, sales_rep.id, sales_rep.full_name)
        ).subquery()

        return (
            select(
                per_user_agg.c.quote_id,
                func.jsonb_agg(
                    func.jsonb_build_object(
                        text("'full_name'"),
                        per_user_agg.c.full_name,
                        text("'total'"),
                        per_user_agg.c.total,
                        text("'avg_split_rate'"),
                        per_user_agg.c.avg_split_rate,
                    )
                ).label("sales_reps"),
            )
            .select_from(per_user_agg)
            .group_by(per_user_agg.c.quote_id)
        ).subquery()

    def paginated_stmt(self) -> Select[Any]:
        sold_to = aliased(Customer)
        end_user = aliased(Customer)

        empty_str_array = cast(text("ARRAY[]::text[]"), ARRAY(String))

        end_users_agg = func.coalesce(
            array_agg(end_user.company_name.distinct()).filter(
                end_user.company_name.isnot(None)
            ),
            empty_str_array,
        ).label("end_users")

        factories_agg = func.coalesce(
            array_agg(Factory.title.distinct()).filter(Factory.title.isnot(None)),
            empty_str_array,
        ).label("factories")

        categories_agg = func.coalesce(
            array_agg(ProductCategory.title.distinct()).filter(
                ProductCategory.title.isnot(None)
            ),
            empty_str_array,
        ).label("categories")

        part_numbers_agg = func.coalesce(
            array_agg(
                func.coalesce(
                    Product.factory_part_number, QuoteDetail.product_name_adhoc
                ).distinct()
            ).filter(
                func.coalesce(
                    Product.factory_part_number, QuoteDetail.product_name_adhoc
                ).isnot(None)
            ),
            empty_str_array,
        ).label("part_numbers")

        sales_reps_subq = self._sales_reps_subquery()
        sales_reps_agg = func.coalesce(
            sales_reps_subq.c.sales_reps,
            cast(text("'[]'"), JSONB),
        ).label("sales_reps")

        return (
            select(
                Quote.id,
                Quote.created_at,
                User.full_name.label("created_by"),
                Quote.quote_number,
                Quote.status,
                Quote.pipeline_stage,
                Quote.entity_date,
                Quote.exp_date,
                QuoteBalance.total.label("total"),
                QuoteBalance.commission.label("commission"),
                Quote.published,
                Quote.user_ids,
                sold_to.company_name.label("sold_to_customer_name"),
                end_users_agg,
                factories_agg,
                categories_agg,
                part_numbers_agg,
                sales_reps_agg,
            )
            .select_from(Quote)
            .options(lazyload("*"))
            .join(User, User.id == Quote.created_by_id)
            .join(QuoteBalance, QuoteBalance.id == Quote.balance_id)
            .join(sold_to, sold_to.id == Quote.sold_to_customer_id)
            .outerjoin(QuoteDetail, QuoteDetail.quote_id == Quote.id)
            .outerjoin(end_user, end_user.id == QuoteDetail.end_user_id)
            .outerjoin(Factory, Factory.id == QuoteDetail.factory_id)
            .outerjoin(Product, Product.id == QuoteDetail.product_id)
            .outerjoin(
                ProductCategory, ProductCategory.id == Product.product_category_id
            )
            .outerjoin(sales_reps_subq, sales_reps_subq.c.quote_id == Quote.id)
            .group_by(
                Quote.id,
                Quote.created_at,
                User.first_name,
                User.last_name,
                Quote.quote_number,
                Quote.status,
                Quote.pipeline_stage,
                Quote.entity_date,
                Quote.exp_date,
                QuoteBalance.total,
                QuoteBalance.commission,
                Quote.published,
                Quote.user_ids,
                sold_to.company_name,
                sales_reps_subq.c.sales_reps,
            )
        )

    @override
    def compute_user_ids(self, quote: Quote) -> list[UUID]:
        user_ids: set[UUID] = {self.auth_info.flow_user_id}
        for detail in quote.details:
            for split_rate in detail.outside_split_rates:
                user_ids.add(split_rate.user_id)
            for inside_rep in detail.inside_split_rates:
                user_ids.add(inside_rep.user_id)
        return list(user_ids)

    async def find_quote_by_id(self, quote_id: UUID) -> Quote:
        quote = await self.get_by_id(
            quote_id,
            options=[
                joinedload(Quote.details),
                joinedload(Quote.details).joinedload(QuoteDetail.product),
                joinedload(Quote.details).joinedload(QuoteDetail.outside_split_rates),
                joinedload(Quote.details).joinedload(QuoteDetail.inside_split_rates),
                joinedload(Quote.details).joinedload(QuoteDetail.uom),
                joinedload(Quote.details).joinedload(QuoteDetail.order),
                joinedload(Quote.details).joinedload(QuoteDetail.factory),
                joinedload(Quote.details).joinedload(QuoteDetail.end_user),
                joinedload(Quote.balance),
                joinedload(Quote.sold_to_customer),
                joinedload(Quote.bill_to_customer),
                joinedload(Quote.created_by),
                joinedload(Quote.job),
                lazyload("*"),
            ],
        )
        if not quote:
            raise NotFoundError(str(quote_id))
        return quote

    async def create_with_balance(self, quote: Quote) -> Quote:
        balance = await self.balance_repository.create_from_details(quote.details)
        quote.balance_id = balance.id
        _ = await self.create(quote)
        return await self.find_quote_by_id(quote.id)

    async def update_with_balance(self, quote: Quote) -> Quote:
        updated = await self.update(quote)
        _ = await self.balance_repository.recalculate_balance(
            updated.balance_id, updated.details
        )
        await self.session.flush()
        return await self.find_quote_by_id(updated.id)

    async def quote_number_exists(self, quote_number: str) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(Quote)
            .where(Quote.quote_number == quote_number)
        )
        return result.scalar_one() > 0

    async def search_by_quote_number(
        self, search_term: str, limit: int = 20
    ) -> list[Quote]:
        stmt = (
            select(Quote)
            .options(lazyload("*"))
            .where(Quote.quote_number.ilike(f"%{search_term}%"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_job_id(self, job_id: UUID) -> list[Quote]:
        stmt = (
            select(Quote)
            .options(lazyload("*"))
            .join(
                LinkRelation,
                or_(
                    (
                        (LinkRelation.source_entity_type == EntityType.QUOTE)
                        & (LinkRelation.target_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_id == job_id)
                        & (LinkRelation.source_entity_id == Quote.id)
                    ),
                    (
                        (LinkRelation.source_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_type == EntityType.QUOTE)
                        & (LinkRelation.source_entity_id == job_id)
                        & (LinkRelation.target_entity_id == Quote.id)
                    ),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_detail_order_ids(
        self, detail_ids: list[UUID], order_id: UUID
    ) -> None:
        stmt = (
            update(QuoteDetail)
            .where(QuoteDetail.id.in_(detail_ids))
            .values(order_id=order_id)
        )
        _ = await self.session.execute(stmt)

    async def find_by_sold_to_customer_id(self, customer_id: UUID) -> list[Quote]:
        stmt = (
            select(Quote)
            .options(lazyload("*"))
            .where(Quote.sold_to_customer_id == customer_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
