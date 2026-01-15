from uuid import UUID

from commons.db.v6.commission import Adjustment, Check, Credit, Invoice
from commons.db.v6.commission.checks.enums.adjustment_status import AdjustmentStatus
from commons.db.v6.commission.credits.enums import CreditStatus
from commons.db.v6.commission.invoices.invoice import InvoiceStatus
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent
from app.errors.common_errors import ValidationError


class ValidateCheckEntitiesProcessor(BaseProcessor[Check]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE]

    async def process(self, context: EntityContext[Check]) -> None:
        check = context.entity
        if not check.details:
            return

        existing_invoice_ids: set[UUID] = set()
        existing_credit_ids: set[UUID] = set()
        existing_adjustment_ids: set[UUID] = set()

        if context.original_entity and context.original_entity.details:
            for d in context.original_entity.details:
                if d.invoice_id:
                    existing_invoice_ids.add(d.invoice_id)
                if d.credit_id:
                    existing_credit_ids.add(d.credit_id)
                if d.adjustment_id:
                    existing_adjustment_ids.add(d.adjustment_id)

        await self._validate_invoices(check, existing_invoice_ids)
        await self._validate_credits(check, existing_credit_ids)
        await self._validate_adjustments(check, existing_adjustment_ids)

    async def _validate_invoices(self, check: Check, existing_ids: set[UUID]) -> None:
        new_ids = [
            d.invoice_id
            for d in check.details
            if d.invoice_id is not None and d.invoice_id not in existing_ids
        ]
        if not new_ids:
            return

        result = await self.session.execute(
            select(Invoice.invoice_number).where(
                Invoice.id.in_(new_ids),
                or_(Invoice.locked.is_(True), Invoice.status.is_(InvoiceStatus.PAID)),
            )
        )
        invalid = list(result.scalars().all())
        if invalid:
            raise ValidationError(
                f"Cannot add locked or paid invoices to check: {', '.join(invalid)}"
            )

    async def _validate_credits(self, check: Check, existing_ids: set[UUID]) -> None:
        new_ids = [
            d.credit_id
            for d in check.details
            if d.credit_id is not None and d.credit_id not in existing_ids
        ]
        if not new_ids:
            return

        result = await self.session.execute(
            select(Credit.credit_number).where(
                Credit.id.in_(new_ids),
                or_(Credit.locked.is_(True), Credit.status.is_(CreditStatus.POSTED)),
            )
        )
        invalid = list(result.scalars().all())
        if invalid:
            raise ValidationError(
                f"Cannot add locked or posted credits to check: {', '.join(invalid)}"
            )

    async def _validate_adjustments(
        self, check: Check, existing_ids: set[UUID]
    ) -> None:
        new_ids = [
            d.adjustment_id
            for d in check.details
            if d.adjustment_id is not None and d.adjustment_id not in existing_ids
        ]
        if not new_ids:
            return

        result = await self.session.execute(
            select(Adjustment.adjustment_number).where(
                Adjustment.id.in_(new_ids),
                or_(
                    Adjustment.locked.is_(True),
                    Adjustment.status.is_(AdjustmentStatus.POSTED),
                ),
            )
        )
        invalid = list(result.scalars().all())
        if invalid:
            raise ValidationError(
                f"Cannot add locked or posted adjustments to check: {', '.join(invalid)}"
            )
