from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.commission import Adjustment, Check, Credit, Invoice
from commons.db.v6.commission.checks.enums import CheckStatus
from commons.db.v6.commission.checks.enums.adjustment_status import AdjustmentStatus
from commons.db.v6.commission.credits.enums import CreditStatus
from commons.db.v6.commission.invoices.invoice import InvoiceStatus
from commons.db.v6.crm.links.entity_type import EntityType
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.checks.repositories.checks_repository import ChecksRepository
from app.graphql.checks.strawberry.check_input import CheckInput


class CheckService:
    def __init__(
        self,
        repository: ChecksRepository,
        auth_info: AuthInfo,
        session: AsyncSession,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info
        self.session = session

    async def find_check_by_id(self, check_id: UUID) -> Check:
        return await self.repository.find_check_by_id(check_id)

    async def create_check(self, check_input: CheckInput) -> Check:
        if await self.repository.check_number_exists(
            check_input.factory_id, check_input.check_number
        ):
            raise NameAlreadyExistsError(check_input.check_number)

        check = check_input.to_orm_model()
        created = await self.repository.create(check)
        return await self.repository.find_check_by_id(created.id)

    async def update_check(self, check_input: CheckInput) -> Check:
        if check_input.id is None:
            raise ValueError("ID must be provided for update")

        existing_check = await self.repository.find_check_by_id(check_input.id)

        if existing_check.status == CheckStatus.POSTED:
            raise ValueError("Posted checks cannot be updated")

        check = check_input.to_orm_model()
        check.id = check_input.id
        updated = await self.repository.update(check)
        return await self.repository.find_check_by_id(updated.id)

    async def delete_check(self, check_id: UUID) -> bool:
        if not await self.repository.exists(check_id):
            raise NotFoundError(str(check_id))
        return await self.repository.delete(check_id)

    async def search_checks(self, search_term: str, limit: int = 20) -> list[Check]:
        return await self.repository.search_by_check_number(search_term, limit)

    async def find_checks_by_job_id(self, job_id: UUID) -> list[Check]:
        return await self.repository.find_by_job_id(job_id)

    async def find_by_factory_id(self, factory_id: UUID) -> list[Check]:
        return await self.repository.find_by_factory_id(factory_id)

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Check]:
        return await self.repository.find_by_entity(entity_type, entity_id)

    async def unpost_check(self, check_id: UUID) -> Check:
        check = await self.repository.find_check_by_id(check_id)
        if check.status != CheckStatus.POSTED:
            raise ValueError("Check must be in POSTED status to unpost")

        check.status = CheckStatus.OPEN
        _ = await self.repository.update(check)

        await self._revert_invoices_to_open(check)
        await self._revert_credits_to_pending(check)
        await self._revert_adjustments_to_pending(check)
        await self.session.flush()

        return await self.repository.find_check_by_id(check_id)

    async def post_check(self, check_id: UUID) -> Check:
        check = await self.repository.find_check_by_id(check_id)
        if check.status == CheckStatus.POSTED:
            raise ValueError("Check is already posted")

        check.status = CheckStatus.POSTED
        _ = await self.repository.update(check)

        await self._update_invoices_to_paid(check)
        await self._update_credits_to_posted(check)
        await self._update_adjustments_to_posted(check)
        await self.session.flush()

        return await self.repository.find_check_by_id(check_id)

    async def _update_invoices_to_paid(self, check: Check) -> None:
        invoice_ids = [d.invoice_id for d in check.details if d.invoice_id is not None]
        if not invoice_ids:
            return
        _ = await self.session.execute(
            update(Invoice)
            .where(Invoice.id.in_(invoice_ids))
            .values(status=InvoiceStatus.PAID, locked=False)
        )

    async def _update_credits_to_posted(self, check: Check) -> None:
        credit_ids = [d.credit_id for d in check.details if d.credit_id is not None]
        if not credit_ids:
            return
        _ = await self.session.execute(
            update(Credit)
            .where(Credit.id.in_(credit_ids))
            .values(status=CreditStatus.POSTED, locked=False)
        )

    async def _update_adjustments_to_posted(self, check: Check) -> None:
        adjustment_ids = [
            d.adjustment_id for d in check.details if d.adjustment_id is not None
        ]
        if not adjustment_ids:
            return
        _ = await self.session.execute(
            update(Adjustment)
            .where(Adjustment.id.in_(adjustment_ids))
            .values(status=AdjustmentStatus.POSTED, locked=False)
        )

    async def _revert_invoices_to_open(self, check: Check) -> None:
        invoice_ids = [d.invoice_id for d in check.details if d.invoice_id is not None]
        if not invoice_ids:
            return

        _ = await self.session.execute(
            update(Invoice)
            .where(Invoice.id.in_(invoice_ids))
            .values(status=InvoiceStatus.OPEN, locked=True)
        )

    async def _revert_credits_to_pending(self, check: Check) -> None:
        credit_ids = [d.credit_id for d in check.details if d.credit_id is not None]
        if not credit_ids:
            return

        _ = await self.session.execute(
            update(Credit)
            .where(Credit.id.in_(credit_ids))
            .values(status=CreditStatus.PENDING, locked=True)
        )

    async def _revert_adjustments_to_pending(self, check: Check) -> None:
        adjustment_ids = [
            d.adjustment_id for d in check.details if d.adjustment_id is not None
        ]
        if not adjustment_ids:
            return

        _ = await self.session.execute(
            update(Adjustment)
            .where(Adjustment.id.in_(adjustment_ids))
            .values(status=AdjustmentStatus.PENDING, locked=True)
        )
