from commons.db.v6.commission import Invoice
from commons.db.v6.commission.invoices.invoice import InvoiceStatus

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent
from app.errors.common_errors import ValidationError


class ValidateInvoiceStatusProcessor(BaseProcessor[Invoice]):
    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_UPDATE, RepositoryEvent.PRE_DELETE]

    async def process(self, context: EntityContext[Invoice]) -> None:
        original = context.original_entity
        if original is None:
            return

        if original.status == InvoiceStatus.PAID:
            raise ValidationError(
                f"Cannot modify invoice '{original.invoice_number}': invoice is paid"
            )

        if original.locked:
            raise ValidationError(
                f"Cannot modify invoice '{original.invoice_number}': invoice is locked"
            )
