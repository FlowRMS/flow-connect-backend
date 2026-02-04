from typing import Any, override
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.commission.statements import (
    CommissionStatement,
    CommissionStatementBalance,
    CommissionStatementDetail,
    CommissionStatementSplitRate,
)
from commons.db.v6.core import Factory
from commons.db.v6.crm.links.entity_type import EntityType
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.exceptions import NotFoundError
from app.graphql.base_repository import BaseRepository
from app.graphql.statements.repositories.statement_balance_repository import (
    StatementBalanceRepository,
)
from app.graphql.statements.strawberry.statement_landing_page_response import (
    StatementLandingPageResponse,
)
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService


class StatementsRepository(BaseRepository[CommissionStatement]):
    entity_type = EntityType.COMMISSION_STATEMENTS
    landing_model = StatementLandingPageResponse
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.CHECK

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        balance_repository: StatementBalanceRepository,
        rbac_filter_service: RbacFilterService,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            CommissionStatement,
            rbac_filter_service=rbac_filter_service,
        )
        self.balance_repository = balance_repository

    def paginated_stmt(self) -> Select[Any]:
        return (
            select(
                CommissionStatement.id,
                CommissionStatement.created_at,
                User.full_name.label("created_by"),
                CommissionStatement.statement_number,
                CommissionStatement.entity_date,
                CommissionStatementBalance.total.label("total"),
                CommissionStatementBalance.commission,
                Factory.title.label("factory_name"),
                CommissionStatement.user_ids,
            )
            .select_from(CommissionStatement)
            .options(lazyload("*"))
            .join(User, User.id == CommissionStatement.created_by_id)
            .join(
                CommissionStatementBalance,
                CommissionStatementBalance.id == CommissionStatement.balance_id,
            )
            .join(Factory, Factory.id == CommissionStatement.factory_id)
        )

    @override
    def compute_user_ids(self, statement: CommissionStatement) -> list[UUID]:
        user_ids: set[UUID] = {self.auth_info.flow_user_id}
        for detail in statement.details:
            for split_rate in detail.outside_split_rates:
                user_ids.add(split_rate.user_id)
        return list(user_ids)

    async def find_statement_by_id(self, statement_id: UUID) -> CommissionStatement:
        statement = await self.get_by_id(
            statement_id,
            options=[
                joinedload(CommissionStatement.details),
                joinedload(CommissionStatement.details).joinedload(
                    CommissionStatementDetail.end_user
                ),
                joinedload(CommissionStatement.details).joinedload(
                    CommissionStatementDetail.sold_to_customer
                ),
                joinedload(CommissionStatement.details).joinedload(
                    CommissionStatementDetail.order
                ),
                joinedload(CommissionStatement.details).joinedload(
                    CommissionStatementDetail.order_detail
                ),
                joinedload(CommissionStatement.details).joinedload(
                    CommissionStatementDetail.invoice
                ),
                joinedload(CommissionStatement.details).joinedload(
                    CommissionStatementDetail.product
                ),
                joinedload(CommissionStatement.details).joinedload(
                    CommissionStatementDetail.uom
                ),
                joinedload(CommissionStatement.details).joinedload(
                    CommissionStatementDetail.outside_split_rates
                ),
                joinedload(CommissionStatement.details)
                .joinedload(CommissionStatementDetail.outside_split_rates)
                .joinedload(CommissionStatementSplitRate.user),
                joinedload(CommissionStatement.balance),
                joinedload(CommissionStatement.factory),
                joinedload(CommissionStatement.created_by),
                lazyload("*"),
            ],
        )
        if not statement:
            raise NotFoundError(str(statement_id))
        return statement

    async def create_with_balance(
        self, statement: CommissionStatement
    ) -> CommissionStatement:
        balance = await self.balance_repository.create_from_details(statement.details)
        statement.balance_id = balance.id
        _ = await self.create(statement)
        return await self.find_statement_by_id(statement.id)

    async def update_with_balance(
        self, statement: CommissionStatement
    ) -> CommissionStatement:
        updated = await self.update(statement)
        _ = await self.balance_repository.recalculate_balance(
            updated.balance_id, updated.details
        )
        await self.session.flush()
        return await self.find_statement_by_id(updated.id)

    async def statement_number_exists(
        self, factory_id: UUID, statement_number: str
    ) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(CommissionStatement)
            .options(lazyload("*"))
            .where(
                CommissionStatement.factory_id == factory_id,
                CommissionStatement.statement_number == statement_number,
            )
        )
        return result.scalar_one() > 0

    async def find_by_statement_number(
        self, factory_id: UUID, statement_number: str
    ) -> CommissionStatement | None:
        stmt = (
            select(CommissionStatement)
            .options(lazyload("*"))
            .where(
                CommissionStatement.factory_id == factory_id,
                CommissionStatement.statement_number == statement_number,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_by_statement_number(
        self,
        search_term: str,
        limit: int = 20,
    ) -> list[CommissionStatement]:
        stmt = (
            select(CommissionStatement)
            .options(lazyload("*"))
            .where(CommissionStatement.statement_number.ilike(f"%{search_term}%"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_factory_id(
        self, factory_id: UUID, limit: int = 25
    ) -> list[CommissionStatement]:
        stmt = (
            select(CommissionStatement)
            .options(lazyload("*"))
            .where(CommissionStatement.factory_id == factory_id)
            .order_by(CommissionStatement.entity_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
