from uuid import UUID

from commons.db.v6.commission import Deduction, DeductionSplitRate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.exceptions import NotFoundError
from app.core.processors import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.deductions.processors.validate_deduction_status_processor import (
    ValidateDeductionStatusProcessor,
)


class DeductionsRepository(BaseRepository[Deduction]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        processor_executor: ProcessorExecutor,
        validate_status_processor: ValidateDeductionStatusProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Deduction,
            processor_executor=processor_executor,
            processor_executor_classes=[
                validate_status_processor,
            ],
        )

    async def find_deduction_by_id(self, deduction_id: UUID) -> Deduction:
        deduction = await self.get_by_id(
            deduction_id,
            options=[
                joinedload(Deduction.split_rates),
                joinedload(Deduction.split_rates).joinedload(DeductionSplitRate.user),
                joinedload(Deduction.factory),
                joinedload(Deduction.created_by),
                lazyload("*"),
            ],
        )
        if not deduction:
            raise NotFoundError(str(deduction_id))
        return deduction

    async def find_by_check_id(self, check_id: UUID) -> list[Deduction]:
        stmt = (
            select(Deduction)
            .options(
                joinedload(Deduction.split_rates),
                joinedload(Deduction.factory),
                lazyload("*"),
            )
            .where(Deduction.check_id == check_id)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_factory_id(self, factory_id: UUID) -> list[Deduction]:
        stmt = (
            select(Deduction)
            .options(lazyload("*"))
            .where(Deduction.factory_id == factory_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_reason(
        self, search_term: str, limit: int = 20
    ) -> list[Deduction]:
        stmt = (
            select(Deduction)
            .options(lazyload("*"))
            .where(Deduction.reason.ilike(f"%{search_term}%"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
