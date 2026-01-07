from commons.db.v6.commission import Check, Credit, Invoice
from commons.db.v6.commission.checks.enums import CheckStatus
from commons.db.v6.commission.credits.enums import CreditStatus
from commons.db.v6.commission.invoices.invoice import InvoiceStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent


class PostCheckProcessor(BaseProcessor[Check]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.POST_UPDATE]

    async def process(self, context: EntityContext[Check]) -> None:
        check = context.entity
        original = context.original_entity

        if original is None:
            return

        if original.status == CheckStatus.POSTED:
            return

        if check.status != CheckStatus.POSTED:
            return

        check_with_details = await self._get_check_with_details(check.id)
        if check_with_details is None:
            return

        await self._update_invoices_to_paid(check_with_details)
        await self._update_credits_to_posted(check_with_details)
        await self.session.flush()

    async def _get_check_with_details(self, check_id: object) -> Check | None:
        result = await self.session.execute(
            select(Check).options(joinedload(Check.details)).where(Check.id == check_id)
        )
        return result.unique().scalar_one_or_none()

    async def _update_invoices_to_paid(self, check: Check) -> None:
        invoice_ids = [d.invoice_id for d in check.details if d.invoice_id is not None]
        if not invoice_ids:
            return

        result = await self.session.execute(
            select(Invoice).where(Invoice.id.in_(invoice_ids))
        )
        invoices = result.scalars().all()

        for invoice in invoices:
            invoice.status = InvoiceStatus.PAID
            invoice.locked = False

    async def _update_credits_to_posted(self, check: Check) -> None:
        credit_ids = [d.credit_id for d in check.details if d.credit_id is not None]
        if not credit_ids:
            return

        result = await self.session.execute(
            select(Credit).where(Credit.id.in_(credit_ids))
        )
        credits = result.scalars().all()

        for credit in credits:
            credit.status = CreditStatus.POSTED
            credit.locked = False
