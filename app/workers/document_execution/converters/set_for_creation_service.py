from typing import TYPE_CHECKING
from uuid import UUID

from commons.db.v6.ai.entities.enums import ConfirmationStatus, EntityPendingType
from commons.db.v6.ai.entities.pending_entity import PendingEntity
from commons.dtos.invoice.invoice_dto import InvoiceDTO
from commons.dtos.order.order_dto import OrderDTO
from loguru import logger

from .entity_mapping import EntityMapping

if TYPE_CHECKING:
    from .invoice_converter import InvoiceConverter
    from .order_converter import OrderConverter


class SetForCreationService:
    def __init__(
        self,
        order_converter: "OrderConverter",
        invoice_converter: "InvoiceConverter",
    ) -> None:
        super().__init__()
        self._order_converter = order_converter
        self._invoice_converter = invoice_converter

    async def process_set_for_creation(
        self,
        pending_entities: list[PendingEntity],
        dtos: list[OrderDTO | InvoiceDTO],
        entity_mappings: dict[UUID, EntityMapping],
    ) -> None:
        dto_by_id: dict[UUID, OrderDTO | InvoiceDTO] = {
            dto.internal_uuid: dto for dto in dtos if dto.internal_uuid is not None
        }

        await self._create_orders(pending_entities, dto_by_id, entity_mappings)
        await self._create_invoices(pending_entities, dto_by_id, entity_mappings)

    async def _create_orders(
        self,
        pending_entities: list[PendingEntity],
        dto_by_id: dict[UUID, OrderDTO | InvoiceDTO],
        entity_mappings: dict[UUID, EntityMapping],
    ) -> None:
        order_entities = [
            pe
            for pe in pending_entities
            if pe.confirmation_status == ConfirmationStatus.SET_FOR_CREATION
            and pe.entity_type == EntityPendingType.ORDERS
        ]

        for pe in order_entities:
            order_id = await self._create_order_for_pending_entity(
                pe, dto_by_id, entity_mappings
            )
            if order_id:
                self._update_mappings_with_order_id(entity_mappings, pe, order_id)

    async def _create_order_for_pending_entity(
        self,
        pe: PendingEntity,
        dto_by_id: dict[UUID, OrderDTO | InvoiceDTO],
        entity_mappings: dict[UUID, EntityMapping],
    ) -> UUID | None:
        if not pe.dto_ids:
            logger.warning(f"PendingEntity {pe.id} has no dto_ids for SET_FOR_CREATION")
            return None

        dto_id = pe.dto_ids[0]
        dto = dto_by_id.get(dto_id)

        if not dto:
            logger.warning(f"DTO {dto_id} not found for PendingEntity {pe.id}")
            return None

        if not isinstance(dto, OrderDTO):
            logger.warning(f"DTO {dto_id} is not an OrderDTO for order creation")
            return None

        mapping = entity_mappings.get(dto_id, EntityMapping())

        try:
            result = await self._order_converter.to_input(dto, mapping)
            if result.is_error() or result.value is None:
                logger.error(f"Failed to convert order: {result.unwrap_error()}")
                return None
            order = await self._order_converter.create_entity(result.unwrap())
            logger.info(f"Created order {order.id} for SET_FOR_CREATION")
            return order.id
        except Exception as e:
            logger.error(f"Failed to create order for SET_FOR_CREATION: {e}")
            return None

    async def _create_invoices(
        self,
        pending_entities: list[PendingEntity],
        dto_by_id: dict[UUID, OrderDTO | InvoiceDTO],
        entity_mappings: dict[UUID, EntityMapping],
    ) -> None:
        invoice_entities = [
            pe
            for pe in pending_entities
            if pe.confirmation_status == ConfirmationStatus.SET_FOR_CREATION
            and pe.entity_type == EntityPendingType.INVOICES
        ]

        for pe in invoice_entities:
            invoice_id = await self._create_invoice_for_pending_entity(
                pe, dto_by_id, entity_mappings
            )
            if invoice_id:
                self._update_mappings_with_invoice_id(entity_mappings, pe, invoice_id)

    async def _create_invoice_for_pending_entity(
        self,
        pe: PendingEntity,
        dto_by_id: dict[UUID, OrderDTO | InvoiceDTO],
        entity_mappings: dict[UUID, EntityMapping],
    ) -> UUID | None:
        if not pe.dto_ids:
            logger.warning(f"PendingEntity {pe.id} has no dto_ids for SET_FOR_CREATION")
            return None

        dto_id = pe.dto_ids[0]
        dto = dto_by_id.get(dto_id)

        if not dto:
            logger.warning(f"DTO {dto_id} not found for PendingEntity {pe.id}")
            return None

        if not isinstance(dto, InvoiceDTO):
            logger.warning(f"DTO {dto_id} is not an InvoiceDTO for invoice creation")
            return None

        mapping = entity_mappings.get(dto_id, EntityMapping())

        try:
            result = await self._invoice_converter.to_input(dto, mapping)
            if result.is_error() or result.value is None:
                logger.error(f"Failed to convert invoice: {result.error}")
                return None
            invoice = await self._invoice_converter.create_entity(result.value)
            logger.info(f"Created invoice {invoice.id} for SET_FOR_CREATION")
            return invoice.id
        except Exception as e:
            logger.error(f"Failed to create invoice for SET_FOR_CREATION: {e}")
            return None

    def _update_mappings_with_order_id(
        self,
        entity_mappings: dict[UUID, EntityMapping],
        pe: PendingEntity,
        order_id: UUID,
    ) -> None:
        for dto_id in pe.dto_ids or []:
            mapping = entity_mappings.setdefault(dto_id, EntityMapping())
            mapping.order_id = order_id
            logger.info(f"Updated mapping for DTO {dto_id} with order_id {order_id}")

    def _update_mappings_with_invoice_id(
        self,
        entity_mappings: dict[UUID, EntityMapping],
        pe: PendingEntity,
        invoice_id: UUID,
    ) -> None:
        for dto_id in pe.dto_ids or []:
            mapping = entity_mappings.setdefault(dto_id, EntityMapping())
            mapping.invoice_id = invoice_id
            logger.info(
                f"Updated mapping for DTO {dto_id} with invoice_id {invoice_id}"
            )
