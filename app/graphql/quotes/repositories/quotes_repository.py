from typing import Any, override
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from commons.db.v6.crm.quotes import (
    Quote,
    QuoteBalance,
    QuoteDetail,
    QuoteInsideRep,
    QuoteSplitRate,
)
from sqlalchemy import Select, func, literal, or_, select, update
from sqlalchemy.dialects.postgresql import ARRAY, array
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.exceptions import NotFoundError
from app.core.processors import ProcessorExecutor
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
            ],
        )
        self.balance_repository = balance_repository

    @override
    def get_rbac_filter_strategy(self) -> RbacFilterStrategy | None:
        return QuoteOwnerFilterStrategy(RbacResourceEnum.QUOTE)

    def paginated_stmt(self) -> Select[Any]:
        empty_array = literal([]).cast(ARRAY(PG_UUID))

        inside_rep_user_ids_subq = (
            select(
                QuoteDetail.quote_id,
                func.array_agg(QuoteInsideRep.user_id).label("inside_rep_user_ids"),
            )
            .join(QuoteInsideRep, QuoteInsideRep.quote_detail_id == QuoteDetail.id)
            .group_by(QuoteDetail.quote_id)
            .subquery()
        )

        split_rate_user_ids_subq = (
            select(
                QuoteDetail.quote_id,
                func.array_agg(QuoteSplitRate.user_id.distinct()).label(
                    "split_rate_user_ids"
                ),
            )
            .join(QuoteSplitRate, QuoteSplitRate.quote_detail_id == QuoteDetail.id)
            .group_by(QuoteDetail.quote_id)
            .subquery()
        )

        user_ids_expr = func.array_cat(
            func.array_cat(
                array([Quote.created_by_id]),
                func.coalesce(
                    inside_rep_user_ids_subq.c.inside_rep_user_ids, empty_array
                ),
            ),
            func.coalesce(split_rate_user_ids_subq.c.split_rate_user_ids, empty_array),
        ).label("user_ids")

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
                Quote.published,
                user_ids_expr,
            )
            .select_from(Quote)
            .options(lazyload("*"))
            .join(User, User.id == Quote.created_by_id)
            .join(QuoteBalance, QuoteBalance.id == Quote.balance_id)
            .outerjoin(
                inside_rep_user_ids_subq,
                inside_rep_user_ids_subq.c.quote_id == Quote.id,
            )
            .outerjoin(
                split_rate_user_ids_subq,
                split_rate_user_ids_subq.c.quote_id == Quote.id,
            )
        )

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
