from uuid import UUID

from commons.db.v6.commission import Invoice, Order
from commons.db.v6.commission.invoices.invoice import InvoiceStatus

# from commons.db.v6.commission.orders.enums import OrderStatus
from commons.db.v6.commission.statements import CommissionStatement
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent
from app.errors.common_errors import ValidationError


class ValidateStatementEntitiesProcessor(BaseProcessor[CommissionStatement]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE]

    async def process(self, context: EntityContext[CommissionStatement]) -> None:
        statement = context.entity
        if not statement.details:
            return

        existing_order_ids: set[UUID] = set()
        existing_invoice_ids: set[UUID] = set()

        if context.original_entity and context.original_entity.details:
            for d in context.original_entity.details:
                if d.order_id:
                    existing_order_ids.add(d.order_id)
                if d.invoice_id:
                    existing_invoice_ids.add(d.invoice_id)

        await self._validate_orders(statement, existing_order_ids)
        await self._validate_invoices(statement, existing_invoice_ids)

    async def _validate_orders(
        self, statement: CommissionStatement, existing_ids: set[UUID]
    ) -> None:
        new_ids = [
            d.order_id
            for d in statement.details
            if d.order_id is not None and d.order_id not in existing_ids
        ]
        if not new_ids:
            return

        result = await self.session.execute(
            select(Order.order_number).where(
                Order.id.in_(new_ids),
                # or_(Order.locked == True, Order.status == OrderStatus.CANCELLED),
            )
        )
        invalid = list(result.scalars().all())
        if invalid:
            raise ValidationError(
                f"Cannot add locked or cancelled orders to statement: {', '.join(invalid)}"
            )

    async def _validate_invoices(
        self, statement: CommissionStatement, existing_ids: set[UUID]
    ) -> None:
        new_ids = [
            d.invoice_id
            for d in statement.details
            if d.invoice_id is not None and d.invoice_id not in existing_ids
        ]
        if not new_ids:
            return

        result = await self.session.execute(
            select(Invoice.invoice_number).where(
                Invoice.id.in_(new_ids),
                or_(Invoice.locked == True, Invoice.status == InvoiceStatus.PAID),  # noqa: E712
            )
        )
        invalid = list(result.scalars().all())
        if invalid:
            raise ValidationError(
                f"Cannot add locked or paid invoices to statement: {', '.join(invalid)}"
            )
