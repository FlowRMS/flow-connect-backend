from uuid import UUID

from commons.db.v6.ai.entities.enums import ConfirmationStatus, EntityPendingType
from commons.db.v6.ai.entities.pending_entity import PendingEntity
from commons.dtos.check.check_detail_dto import CheckDetailDTO
from commons.dtos.invoice.invoice_dto import InvoiceDTO
from commons.dtos.order.order_dto import OrderDTO
from loguru import logger

from .adjustment_converter import AdjustmentConverter
from .credit_converter import CreditConverter
from .entity_mapping import EntityMapping
from .invoice_converter import InvoiceConverter
from .order_converter import OrderConverter

type DTOType = OrderDTO | CheckDetailDTO


class SetForCreationService:
    def __init__(
        self,
        order_converter: OrderConverter,
        invoice_converter: InvoiceConverter,
        credit_converter: CreditConverter,
        adjustment_converter: AdjustmentConverter,
    ) -> None:
        super().__init__()
        self._order_converter = order_converter
        self._invoice_converter = invoice_converter
        self._credit_converter = credit_converter
        self._adjustment_converter = adjustment_converter

    async def process_set_for_creation(
        self,
        pending_entities: list[PendingEntity],
        entity_mappings: dict[UUID, EntityMapping],
    ) -> None:
        await self._create_orders(pending_entities, entity_mappings)
        await self._create_invoices(pending_entities, entity_mappings)
        await self._create_credits(pending_entities, entity_mappings)
        await self._create_adjustments(pending_entities, entity_mappings)

    async def _create_orders(
        self,
        pending_entities: list[PendingEntity],
        entity_mappings: dict[UUID, EntityMapping],
    ) -> None:
        order_entities = [
            pe
            for pe in pending_entities
            if pe.confirmation_status == ConfirmationStatus.SET_FOR_CREATION
            and pe.entity_type == EntityPendingType.ORDERS
        ]

        for pe in order_entities:
            order_id = await self._create_order_for_pending_entity(pe, entity_mappings)
            if order_id:
                self._update_mappings_with_order_id(entity_mappings, pe, order_id)

    async def _create_order_for_pending_entity(
        self,
        pe: PendingEntity,
        entity_mappings: dict[UUID, EntityMapping],
    ) -> UUID | None:
        if not pe.dto_ids:
            logger.warning(f"PendingEntity {pe.id} has no dto_ids for SET_FOR_CREATION")
            return None

        dto_id = pe.dto_ids[0]
        dto = OrderDTO.model_validate(pe.extracted_data)
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
                pe, entity_mappings
            )
            if invoice_id:
                self._update_mappings_with_invoice_id(entity_mappings, pe, invoice_id)

    async def _create_invoice_for_pending_entity(
        self,
        pe: PendingEntity,
        entity_mappings: dict[UUID, EntityMapping],
    ) -> UUID | None:
        if not pe.dto_ids:
            logger.warning(f"PendingEntity {pe.id} has no dto_ids for SET_FOR_CREATION")
            return None

        dto_id = pe.dto_ids[0]
        dto = InvoiceDTO.model_validate(pe.extracted_data)
        mapping = entity_mappings.get(dto_id, EntityMapping())

        try:
            result = await self._invoice_converter.to_input(dto, mapping)
            if result.is_error() or result.value is None:
                logger.error(f"Failed to convert invoice: {result.unwrap_error()}")
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
        flow_idx = pe.flow_index_detail if pe.flow_index_detail is not None else 0
        for dto_id in pe.dto_ids or []:
            mapping = entity_mappings.setdefault(dto_id, EntityMapping())
            mapping.orders[flow_idx] = order_id
            logger.info(
                f"Updated mapping for DTO {dto_id} with order_id {order_id} "
                f"at flow_index {flow_idx}"
            )

    def _update_mappings_with_invoice_id(
        self,
        entity_mappings: dict[UUID, EntityMapping],
        pe: PendingEntity,
        invoice_id: UUID,
    ) -> None:
        flow_idx = pe.flow_index_detail if pe.flow_index_detail is not None else 0
        for dto_id in pe.dto_ids or []:
            mapping = entity_mappings.setdefault(dto_id, EntityMapping())
            mapping.invoices[flow_idx] = invoice_id
            logger.info(
                f"Updated mapping for DTO {dto_id} with invoice_id {invoice_id} "
                f"at flow_index {flow_idx}"
            )

    async def _create_credits(
        self,
        pending_entities: list[PendingEntity],
        entity_mappings: dict[UUID, EntityMapping],
    ) -> None:
        credit_entities = [
            pe
            for pe in pending_entities
            if pe.confirmation_status == ConfirmationStatus.SET_FOR_CREATION
            and pe.entity_type == EntityPendingType.CREDITS
        ]

        for pe in credit_entities:
            credit_id = await self._create_credit_for_pending_entity(
                pe, entity_mappings
            )
            if credit_id:
                self._update_mappings_with_credit_id(entity_mappings, pe, credit_id)

    async def _create_credit_for_pending_entity(
        self,
        pe: PendingEntity,
        entity_mappings: dict[UUID, EntityMapping],
    ) -> UUID | None:
        if not pe.dto_ids:
            logger.warning(f"PendingEntity {pe.id} has no dto_ids for SET_FOR_CREATION")
            return None

        dto_id = pe.dto_ids[0]
        dto = CheckDetailDTO.model_validate(pe.extracted_data)

        if not isinstance(dto, CheckDetailDTO):
            logger.warning(f"DTO {dto_id} is not a CheckDetailDTO for credit creation")
            return None

        mapping = entity_mappings.get(dto_id, EntityMapping())

        try:
            result = await self._credit_converter.to_input(dto, mapping)
            if result.is_error() or result.value is None:
                logger.error(f"Failed to convert credit: {result.unwrap_error()}")
                return None
            credit = await self._credit_converter.create_entity(result.value)
            logger.info(f"Created credit {credit.id} for SET_FOR_CREATION")
            return credit.id
        except Exception as e:
            logger.error(f"Failed to create credit for SET_FOR_CREATION: {e}")
            return None

    def _update_mappings_with_credit_id(
        self,
        entity_mappings: dict[UUID, EntityMapping],
        pe: PendingEntity,
        credit_id: UUID,
    ) -> None:
        flow_idx = pe.flow_index_detail if pe.flow_index_detail is not None else 0
        for dto_id in pe.dto_ids or []:
            mapping = entity_mappings.setdefault(dto_id, EntityMapping())
            mapping.credits[flow_idx] = credit_id
            logger.info(
                f"Updated mapping for DTO {dto_id} with credit_id {credit_id} "
                f"at flow_index {flow_idx}"
            )

    async def _create_adjustments(
        self,
        pending_entities: list[PendingEntity],
        entity_mappings: dict[UUID, EntityMapping],
    ) -> None:
        adjustment_entities = [
            pe
            for pe in pending_entities
            if pe.confirmation_status == ConfirmationStatus.SET_FOR_CREATION
            and pe.entity_type == EntityPendingType.ADJUSTMENTS
        ]

        for pe in adjustment_entities:
            adjustment_id = await self._create_adjustment_for_pending_entity(
                pe, entity_mappings
            )
            if adjustment_id:
                self._update_mappings_with_adjustment_id(
                    entity_mappings, pe, adjustment_id
                )

    async def _create_adjustment_for_pending_entity(
        self,
        pe: PendingEntity,
        entity_mappings: dict[UUID, EntityMapping],
    ) -> UUID | None:
        if not pe.dto_ids:
            logger.warning(f"PendingEntity {pe.id} has no dto_ids for SET_FOR_CREATION")
            return None

        dto_id = pe.dto_ids[0]
        dto = CheckDetailDTO.model_validate(pe.extracted_data)
        mapping = entity_mappings.get(dto_id, EntityMapping())

        try:
            result = await self._adjustment_converter.to_input(dto, mapping)
            if result.is_error() or result.value is None:
                logger.error(f"Failed to convert adjustment: {result.unwrap_error()}")
                return None
            adjustment = await self._adjustment_converter.create_entity(result.value)
            logger.info(f"Created adjustment {adjustment.id} for SET_FOR_CREATION")
            return adjustment.id
        except Exception as e:
            logger.error(f"Failed to create adjustment for SET_FOR_CREATION: {e}")
            return None

    def _update_mappings_with_adjustment_id(
        self,
        entity_mappings: dict[UUID, EntityMapping],
        pe: PendingEntity,
        adjustment_id: UUID,
    ) -> None:
        flow_idx = pe.flow_index_detail if pe.flow_index_detail is not None else 0
        for dto_id in pe.dto_ids or []:
            mapping = entity_mappings.setdefault(dto_id, EntityMapping())
            mapping.adjustments[flow_idx] = adjustment_id
            logger.info(
                f"Updated mapping for DTO {dto_id} with adjustment_id {adjustment_id} "
                f"at flow_index {flow_idx}"
            )
