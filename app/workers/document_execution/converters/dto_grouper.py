from dataclasses import dataclass, field
from uuid import UUID

from commons.db.v6.ai.entities.pending_entity import PendingEntity
from commons.dtos.invoice.invoice_dto import InvoiceDTO
from commons.dtos.order.order_dto import OrderDTO

from .entity_mapping import EntityMapping


@dataclass
class GroupedOrderDTO:
    dto: OrderDTO
    pending_entities: list[PendingEntity] = field(default_factory=list)
    dto_ids: list[UUID] = field(default_factory=list)


@dataclass
class GroupedInvoiceDTO:
    dto: InvoiceDTO
    pending_entities: list[PendingEntity] = field(default_factory=list)
    dto_ids: list[UUID] = field(default_factory=list)


def _get_order_group_key(dto: OrderDTO) -> str:
    """
    Create a grouping key for orders based on order_number + sold_to_customer.
    Orders with the same key should be merged into a single order with multiple details.
    """
    parts = []
    if dto.order_number:
        parts.append(dto.order_number.strip().lower())
    if dto.sold_to_customer and dto.sold_to_customer.name:
        parts.append(dto.sold_to_customer.name.strip().lower())
    return "|".join(parts) if parts else str(dto.internal_uuid)


def _get_invoice_group_key(dto: InvoiceDTO) -> str:
    """
    Create a grouping key for invoices based on invoice_number + factory.
    Invoices with the same key should be merged into a single invoice with multiple details.
    """
    parts = []
    if dto.invoice_number:
        parts.append(dto.invoice_number.strip().lower())
    if dto.factory and dto.factory.name:
        parts.append(dto.factory.name.strip().lower())
    return "|".join(parts) if parts else str(dto.internal_uuid)


def group_order_dtos(
    pending_entities: list[PendingEntity],
    entity_mappings: dict[UUID, EntityMapping],
) -> list[GroupedOrderDTO]:
    """
    Group OrderDTOs that should be merged into single orders.
    Groups by order_number + sold_to_customer.
    Returns grouped DTOs with their associated pending entities and mappings.
    """
    groups: dict[str, GroupedOrderDTO] = {}

    for pe in pending_entities:
        if not pe.dto_ids:
            continue

        dto = OrderDTO.model_validate(pe.extracted_data)
        group_key = _get_order_group_key(dto)

        if group_key not in groups:
            merged_dto = OrderDTO(
                internal_uuid=dto.internal_uuid,
                order_number=dto.order_number,
                order_date=dto.order_date,
                due_date=dto.due_date,
                factory=dto.factory,
                sold_to_customer=dto.sold_to_customer,
                bill_to_customer=dto.bill_to_customer,
                shipping_terms=dto.shipping_terms,
                ship_date=dto.ship_date,
                mark_number=dto.mark_number,
                job_name=dto.job_name,
                payment_terms=dto.payment_terms,
                details=[],
            )
            groups[group_key] = GroupedOrderDTO(dto=merged_dto)

        grouped = groups[group_key]
        grouped.pending_entities.append(pe)
        grouped.dto_ids.extend(pe.dto_ids or [])

        for detail in dto.details:
            grouped.dto.details.append(detail)

    return list(groups.values())


def group_invoice_dtos(
    pending_entities: list[PendingEntity],
    entity_mappings: dict[UUID, EntityMapping],
) -> list[GroupedInvoiceDTO]:
    """
    Group InvoiceDTOs that should be merged into single invoices.
    Groups by invoice_number + factory.
    Returns grouped DTOs with their associated pending entities and mappings.
    """
    groups: dict[str, GroupedInvoiceDTO] = {}

    for pe in pending_entities:
        if not pe.dto_ids:
            continue

        dto = InvoiceDTO.model_validate(pe.extracted_data)
        group_key = _get_invoice_group_key(dto)

        if group_key not in groups:
            merged_dto = InvoiceDTO(
                internal_uuid=dto.internal_uuid,
                invoice_number=dto.invoice_number,
                invoice_date=dto.invoice_date,
                invoice_amount=dto.invoice_amount,
                factory=dto.factory,
                sold_to_customer=dto.sold_to_customer,
                bill_to_customer=dto.bill_to_customer,
                order=dto.order,
                details=[],
            )
            groups[group_key] = GroupedInvoiceDTO(dto=merged_dto)

        grouped = groups[group_key]
        grouped.pending_entities.append(pe)
        grouped.dto_ids.extend(pe.dto_ids or [])

        for detail in dto.details:
            grouped.dto.details.append(detail)

        if dto.invoice_amount and grouped.dto.invoice_amount:
            grouped.dto.invoice_amount += dto.invoice_amount
        elif dto.invoice_amount:
            grouped.dto.invoice_amount = dto.invoice_amount

    return list(groups.values())
