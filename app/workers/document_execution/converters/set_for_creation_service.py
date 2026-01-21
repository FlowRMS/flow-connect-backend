from uuid import UUID

from commons.db.v6.ai.entities.pending_entity import PendingEntity
from loguru import logger

from .adjustment_creation_handler import AdjustmentCreationHandler
from .creation_types import CreationResult
from .credit_creation_handler import CreditCreationHandler
from .entity_mapping import EntityMapping
from .invoice_creation_handler import InvoiceCreationHandler
from .order_creation_handler import OrderCreationHandler


class SetForCreationService:
    def __init__(
        self,
        order_creation_handler: OrderCreationHandler,
        invoice_creation_handler: InvoiceCreationHandler,
        credit_creation_handler: CreditCreationHandler,
        adjustment_creation_handler: AdjustmentCreationHandler,
    ) -> None:
        super().__init__()
        self._order_handler = order_creation_handler
        self._invoice_handler = invoice_creation_handler
        self._credit_handler = credit_creation_handler
        self._adjustment_handler = adjustment_creation_handler

    async def process_set_for_creation(
        self,
        pending_entities: list[PendingEntity],
        entity_mappings: dict[UUID, EntityMapping],
    ) -> CreationResult:
        result = CreationResult()

        result.orders_created = await self._order_handler.create_orders(
            pending_entities, entity_mappings, result
        )
        if result.has_issues:
            return result

        logger.debug(
            f"Orders created: {result.orders_created}. Proceeding to invoice creation."
        )

        result.invoices_created = await self._invoice_handler.create_invoices(
            pending_entities, entity_mappings, result
        )

        logger.debug(
            f"Invoices created: {result.invoices_created}. Proceeding to credit creation."
        )

        if result.has_issues:
            return result

        result.credits_created = await self._credit_handler.create_credits(
            pending_entities, entity_mappings, result
        )
        if result.has_issues:
            return result

        result.adjustments_created = await self._adjustment_handler.create_adjustments(
            pending_entities, entity_mappings, result
        )

        return result
