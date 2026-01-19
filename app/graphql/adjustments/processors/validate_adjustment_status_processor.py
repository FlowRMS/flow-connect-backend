from commons.db.v6.commission import Adjustment, Check
from commons.db.v6.commission.checks.enums.adjustment_status import AdjustmentStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent
from app.errors.common_errors import ValidationError


class ValidateAdjustmentStatusProcessor(BaseProcessor[Adjustment]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_UPDATE, RepositoryEvent.PRE_DELETE]

    async def process(self, context: EntityContext[Adjustment]) -> None:
        original = context.original_entity
        if original is None:
            return

        if original.status == AdjustmentStatus.POSTED:
            raise ValidationError("Cannot modify a posted adjustment.")

    async def _get_check(self, check_id: object) -> Check | None:
        result = await self.session.execute(select(Check).where(Check.id == check_id))
        return result.scalar_one_or_none()
