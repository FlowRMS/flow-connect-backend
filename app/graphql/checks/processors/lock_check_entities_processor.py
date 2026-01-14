from dataclasses import dataclass, field
from uuid import UUID

from commons.db.v6.commission import Adjustment, Check, Credit, Invoice
from commons.db.v6.commission.checks.enums import CheckStatus
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent


@dataclass
class CheckEntityIds:
    invoices: set[UUID] = field(default_factory=set)
    credits: set[UUID] = field(default_factory=set)
    adjustments: set[UUID] = field(default_factory=set)


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

        original_ids = self._extract_entity_ids(context.original_entity)
        current_ids = self._extract_entity_ids(check_with_details)

        await self._lock_new_entities(original_ids, current_ids)
        await self._unlock_removed_entities(original_ids, current_ids)

    async def _get_check_with_details(self, check_id: object) -> Check | None:
        result = await self.session.execute(
            select(Check).options(joinedload(Check.details)).where(Check.id == check_id)
        )
        return result.unique().scalar_one_or_none()

    def _extract_entity_ids(self, check: Check | None) -> CheckEntityIds:
        if check is None or not check.details:
            return CheckEntityIds()

        return CheckEntityIds(
            invoices={d.invoice_id for d in check.details if d.invoice_id},
            credits={d.credit_id for d in check.details if d.credit_id},
            adjustments={d.adjustment_id for d in check.details if d.adjustment_id},
        )

    async def _lock_new_entities(
        self,
        original: CheckEntityIds,
        current: CheckEntityIds,
    ) -> None:
        new_invoice_ids = current.invoices - original.invoices
        new_credit_ids = current.credits - original.credits
        new_adjustment_ids = current.adjustments - original.adjustments

        if new_invoice_ids:
            _ = await self.session.execute(
                update(Invoice)
                .where(Invoice.id.in_(new_invoice_ids))
                .values(locked=True)
            )
        if new_credit_ids:
            _ = await self.session.execute(
                update(Credit).where(Credit.id.in_(new_credit_ids)).values(locked=True)
            )
        if new_adjustment_ids:
            _ = await self.session.execute(
                update(Adjustment)
                .where(Adjustment.id.in_(new_adjustment_ids))
                .values(locked=True)
            )

    async def _unlock_removed_entities(
        self,
        original: CheckEntityIds,
        current: CheckEntityIds,
    ) -> None:
        removed_invoice_ids = original.invoices - current.invoices
        removed_credit_ids = original.credits - current.credits
        removed_adjustment_ids = original.adjustments - current.adjustments

        if removed_invoice_ids:
            _ = await self.session.execute(
                update(Invoice)
                .where(Invoice.id.in_(removed_invoice_ids))
                .values(locked=False)
            )
        if removed_credit_ids:
            _ = await self.session.execute(
                update(Credit)
                .where(Credit.id.in_(removed_credit_ids))
                .values(locked=False)
            )
        if removed_adjustment_ids:
            _ = await self.session.execute(
                update(Adjustment)
                .where(Adjustment.id.in_(removed_adjustment_ids))
                .values(locked=False)
            )
