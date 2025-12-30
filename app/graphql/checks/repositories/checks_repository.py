from uuid import UUID

from commons.db.v6.commission import Check, CheckDetail
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, lazyload

from app.core.context_wrapper import ContextWrapper
from app.core.exceptions import NotFoundError
from app.core.processors import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.checks.processors.post_check_processor import PostCheckProcessor
from app.graphql.checks.processors.validate_check_status_processor import (
    ValidateCheckStatusProcessor,
)


class ChecksRepository(BaseRepository[Check]):
    entity_type = EntityType.CHECK

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        processor_executor: ProcessorExecutor,
        validate_status_processor: ValidateCheckStatusProcessor,
        post_check_processor: PostCheckProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Check,
            processor_executor=processor_executor,
            processor_executor_classes=[
                validate_status_processor,
                post_check_processor,
            ],
        )

    async def find_check_by_id(self, check_id: UUID) -> Check:
        check = await self.get_by_id(
            check_id,
            options=[
                joinedload(Check.details),
                joinedload(Check.details).joinedload(CheckDetail.invoice),
                joinedload(Check.details).joinedload(CheckDetail.credit),
                joinedload(Check.details).joinedload(CheckDetail.deduction),
                joinedload(Check.factory),
                lazyload("*"),
            ],
        )
        if not check:
            raise NotFoundError(str(check_id))
        return check

    async def check_number_exists(self, factory_id: UUID, check_number: str) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(Check)
            .options(lazyload("*"))
            .where(
                Check.factory_id == factory_id,
                Check.check_number == check_number,
            )
        )
        return result.scalar_one() > 0

    async def search_by_check_number(
        self, search_term: str, limit: int = 20
    ) -> list[Check]:
        stmt = (
            select(Check)
            .options(lazyload("*"))
            .where(Check.check_number.ilike(f"%{search_term}%"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_factory_id(self, factory_id: UUID) -> list[Check]:
        stmt = (
            select(Check).options(lazyload("*")).where(Check.factory_id == factory_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_job_id(self, job_id: UUID) -> list[Check]:
        stmt = (
            select(Check)
            .options(lazyload("*"))
            .join(
                LinkRelation,
                or_(
                    (
                        (LinkRelation.source_entity_type == EntityType.CHECK)
                        & (LinkRelation.target_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_id == job_id)
                        & (LinkRelation.source_entity_id == Check.id)
                    ),
                    (
                        (LinkRelation.source_entity_type == EntityType.JOB)
                        & (LinkRelation.target_entity_type == EntityType.CHECK)
                        & (LinkRelation.source_entity_id == job_id)
                        & (LinkRelation.target_entity_id == Check.id)
                    ),
                ),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
