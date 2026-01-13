from uuid import UUID

from commons.db.v6.ai.entities.enums import ConfirmationStatus, EntityPendingType
from commons.db.v6.ai.entities.pending_entity import PendingEntity
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from .creation_types import CreationIssue, CreationResult
from .dto_grouper import GroupedInvoiceDTO, group_invoice_dtos
from .entity_mapping import EntityMapping
from .invoice_converter import InvoiceConverter


class InvoiceCreationHandler:
    def __init__(
        self,
        session: AsyncSession,
        invoice_converter: InvoiceConverter,
    ) -> None:
        super().__init__()
        self._session = session
        self._invoice_converter = invoice_converter

    async def create_invoices(
        self,
        pending_entities: list[PendingEntity],
        entity_mappings: dict[UUID, EntityMapping],
        result: CreationResult,
    ) -> int:
        invoice_entities = [
            pe
            for pe in pending_entities
            if pe.confirmation_status == ConfirmationStatus.SET_FOR_CREATION
            and pe.entity_type == EntityPendingType.INVOICES
        ]

        if not invoice_entities:
            return 0

        grouped_invoices = group_invoice_dtos(invoice_entities, entity_mappings)

        created_count = 0
        for grouped in grouped_invoices:
            invoice_id = await self._create_grouped_invoice(
                grouped, entity_mappings, result
            )
            if invoice_id:
                for pe in grouped.pending_entities:
                    self._update_mappings(entity_mappings, pe, invoice_id)
                created_count += 1

        return created_count

    async def _create_grouped_invoice(
        self,
        grouped: GroupedInvoiceDTO,
        entity_mappings: dict[UUID, EntityMapping],
        result: CreationResult,
    ) -> UUID | None:
        if not grouped.dto_ids:
            logger.warning("Grouped invoice has no dto_ids for SET_FOR_CREATION")
            return None

        first_dto_id = grouped.dto_ids[0]
        mapping = entity_mappings.get(first_dto_id, EntityMapping())
        pe_id = grouped.pending_entities[0].id if grouped.pending_entities else None

        conversion = await self._invoice_converter.to_input(grouped.dto, mapping)
        if conversion.is_error() or conversion.value is None:
            error_msg = str(conversion.unwrap_error())
            logger.exception(f"Failed to convert invoice: {error_msg}")
            result.issues.append(
                CreationIssue(
                    entity_type=EntityPendingType.INVOICES,
                    pending_entity_id=pe_id,
                    error_message=error_msg,
                )
            )
            return None

        async with self._session.begin_nested():
            try:
                invoice = await self._invoice_converter.create_entity(conversion.value)
                logger.info(
                    f"Created invoice {invoice.id} with {len(grouped.dto.details)} "
                    f"details (grouped from {len(grouped.pending_entities)} records)"
                )
                return invoice.id
            except Exception as e:
                logger.exception(f"Failed to create invoice for SET_FOR_CREATION: {e}")
                result.issues.append(
                    CreationIssue(
                        entity_type=EntityPendingType.INVOICES,
                        pending_entity_id=pe_id,
                        error_message=str(e),
                    )
                )
                return None

    def _update_mappings(
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
