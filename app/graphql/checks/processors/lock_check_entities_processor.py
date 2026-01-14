from commons.db.v6.commission import Adjustment, Check, Credit, Invoice
from commons.db.v6.commission.checks.enums import CheckStatus
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent


class LockCheckEntitiesProcessor(BaseProcessor[Check]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.POST_CREATE, RepositoryEvent.POST_UPDATE]

    async def process(self, context: EntityContext[Check]) -> None:
        check = context.entity

        if check.status == CheckStatus.POSTED:
            return

        check_with_details = await self._get_check_with_details(check.id)
        if check_with_details is None:
            return

        await self._lock_invoices(check_with_details)
        await self._lock_credits(check_with_details)
        await self._lock_adjustments(check_with_details)

    async def _get_check_with_details(self, check_id: object) -> Check | None:
        result = await self.session.execute(
            select(Check).options(joinedload(Check.details)).where(Check.id == check_id)
        )
        return result.unique().scalar_one_or_none()

    async def _lock_invoices(self, check: Check) -> None:
        invoice_ids = [d.invoice_id for d in check.details if d.invoice_id is not None]
        if not invoice_ids:
            return
        _ = await self.session.execute(
            update(Invoice).where(Invoice.id.in_(invoice_ids)).values(locked=True)
        )

    async def _lock_credits(self, check: Check) -> None:
        credit_ids = [d.credit_id for d in check.details if d.credit_id is not None]
        if not credit_ids:
            return
        _ = await self.session.execute(
            update(Credit).where(Credit.id.in_(credit_ids)).values(locked=True)
        )

    async def _lock_adjustments(self, check: Check) -> None:
        adjustment_ids = [
            d.adjustment_id for d in check.details if d.adjustment_id is not None
        ]
        if not adjustment_ids:
            return
        _ = await self.session.execute(
            update(Adjustment)
            .where(Adjustment.id.in_(adjustment_ids))
            .values(locked=True)
        )
