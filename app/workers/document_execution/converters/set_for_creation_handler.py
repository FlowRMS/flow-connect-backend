from uuid import UUID

from commons.db.v6.ai.entities.enums import ConfirmationStatus, EntityPendingType
from commons.db.v6.ai.entities.pending_entity import PendingEntity
from loguru import logger

from .entity_mapping import EntityMapping


def get_pending_entities_for_creation(
    pending_entities: list[PendingEntity],
    entity_type: EntityPendingType,
) -> list[PendingEntity]:
    return [
        pe
        for pe in pending_entities
        if pe.confirmation_status == ConfirmationStatus.SET_FOR_CREATION
        and pe.entity_type == entity_type
    ]


def has_orders_for_creation(pending_entities: list[PendingEntity]) -> bool:
    return any(
        pe.confirmation_status == ConfirmationStatus.SET_FOR_CREATION
        and pe.entity_type == EntityPendingType.ORDERS
        for pe in pending_entities
    )


def has_invoices_for_creation(pending_entities: list[PendingEntity]) -> bool:
    return any(
        pe.confirmation_status == ConfirmationStatus.SET_FOR_CREATION
        and pe.entity_type == EntityPendingType.INVOICES
        for pe in pending_entities
    )


def update_mapping_with_order_id(
    mappings: dict[UUID, EntityMapping],
    pending_entity: PendingEntity,
    order_id: UUID,
) -> None:
    for dto_id in pending_entity.dto_ids or []:
        mapping = mappings.setdefault(dto_id, EntityMapping())
        mapping.order_id = order_id
        logger.info(f"Updated mapping for DTO {dto_id} with order_id {order_id}")


def update_mapping_with_invoice_id(
    mappings: dict[UUID, EntityMapping],
    pending_entity: PendingEntity,
    invoice_id: UUID,
) -> None:
    for dto_id in pending_entity.dto_ids or []:
        mapping = mappings.setdefault(dto_id, EntityMapping())
        mapping.invoice_id = invoice_id
        logger.info(f"Updated mapping for DTO {dto_id} with invoice_id {invoice_id}")
