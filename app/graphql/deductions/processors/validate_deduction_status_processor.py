from commons.db.v6.commission import Check, Deduction
from commons.db.v6.commission.checks.enums import CheckStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent
from app.errors.common_errors import ValidationError


class ValidateDeductionStatusProcessor(BaseProcessor[Deduction]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_UPDATE, RepositoryEvent.PRE_DELETE]

    async def process(self, context: EntityContext[Deduction]) -> None:
        original = context.original_entity
        if original is None:
            return

        check = await self._get_check(original.check_id)
        if check is None:
            return

        if check.status == CheckStatus.POSTED:
            raise ValidationError(
                f"Cannot modify deduction: parent check '{check.check_number}' is posted"
            )

    async def _get_check(self, check_id: object) -> Check | None:
        result = await self.session.execute(select(Check).where(Check.id == check_id))
        return result.scalar_one_or_none()
