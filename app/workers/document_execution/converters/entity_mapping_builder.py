from uuid import UUID

from commons.db.v6.ai.entities.enums import ConfirmationStatus, EntityPendingType
from commons.db.v6.ai.entities.pending_entity import PendingEntity
from loguru import logger

from .entity_mapping import EntityMapping

CONFIRMED_STATUSES = frozenset(
    {
        ConfirmationStatus.CONFIRMED,
        ConfirmationStatus.AUTO_MATCHED,
        ConfirmationStatus.CREATED_NEW,
    }
)

SKIPPED_STATUS = ConfirmationStatus.SKIPPED


class EntityMappingBuilder:
    def __init__(self, pending_entities: list[PendingEntity]) -> None:
        super().__init__()
        self._pending_entities = pending_entities
        self._mappings: dict[UUID, EntityMapping] = {}

    def build(self) -> dict[UUID, EntityMapping]:
        logger.info(
            f"Building entity mapping from {len(self._pending_entities)} PendingEntities"
        )
        self._process_base_entities()
        self._process_skipped_entities()
        return self._mappings

    def _process_base_entities(self) -> None:
        for pe in self._pending_entities:
            if pe.confirmation_status not in CONFIRMED_STATUSES:
                continue
            if not pe.best_match_id:
                logger.warning(
                    f"PendingEntity {pe.id} is confirmed but has no best_match_id"
                )
                continue

            self._apply_entity_to_mapping(pe, pe.best_match_id)

    def _process_skipped_entities(self) -> None:
        for pe in self._pending_entities:
            if pe.confirmation_status != SKIPPED_STATUS:
                continue

            match pe.entity_type:
                case EntityPendingType.PRODUCTS:
                    if pe.flow_index_detail is not None:
                        self._mark_product_skipped(pe)
                case EntityPendingType.ORDERS:
                    self._mark_order_skipped(pe)
                case EntityPendingType.INVOICES:
                    self._mark_invoice_skipped(pe)

    def _apply_entity_to_mapping(self, pe: PendingEntity, entity_id: UUID) -> None:
        mapping = EntityMapping()
        flow_idx = pe.flow_index_detail if pe.flow_index_detail is not None else 0

        match pe.entity_type:
            case EntityPendingType.FACTORIES:
                mapping.factory_id = entity_id
            case EntityPendingType.CUSTOMERS:
                mapping.sold_to_customer_id = entity_id
            case EntityPendingType.BILL_TO_CUSTOMERS:
                mapping.bill_to_customer_id = entity_id
            case EntityPendingType.ORDERS:
                mapping.orders[flow_idx] = entity_id
            case EntityPendingType.INVOICES:
                mapping.invoices[flow_idx] = entity_id
            case EntityPendingType.CREDITS:
                mapping.credits[flow_idx] = entity_id
            case EntityPendingType.ADJUSTMENTS:
                mapping.adjustments[flow_idx] = entity_id
            case EntityPendingType.PRODUCTS:
                if pe.flow_index_detail is not None:
                    mapping.products[pe.flow_index_detail] = entity_id
            case EntityPendingType.END_USERS:
                if pe.flow_index_detail is not None:
                    mapping.end_users[pe.flow_index_detail] = entity_id

        for dto_id in pe.dto_ids or []:
            self._merge_mapping(dto_id, mapping)

    def _merge_mapping(self, dto_id: UUID, source: EntityMapping) -> None:
        existing = self._mappings.get(dto_id)
        if existing:
            if source.factory_id:
                existing.factory_id = source.factory_id
            if source.sold_to_customer_id:
                existing.sold_to_customer_id = source.sold_to_customer_id
            if source.bill_to_customer_id:
                existing.bill_to_customer_id = source.bill_to_customer_id
            existing.orders.update(source.orders)
            existing.invoices.update(source.invoices)
            existing.credits.update(source.credits)
            existing.adjustments.update(source.adjustments)
            existing.products.update(source.products)
            existing.end_users.update(source.end_users)
            existing.skipped_product_indices.update(source.skipped_product_indices)
            existing.skipped_order_indices.update(source.skipped_order_indices)
            existing.skipped_invoice_indices.update(source.skipped_invoice_indices)
        else:
            self._mappings[dto_id] = source

    def _mark_product_skipped(self, pe: PendingEntity) -> None:
        if pe.flow_index_detail is None:
            return
        for dto_id in pe.dto_ids or []:
            mapping = self._mappings.setdefault(dto_id, EntityMapping())
            mapping.skipped_product_indices.add(pe.flow_index_detail)

    def _mark_order_skipped(self, pe: PendingEntity) -> None:
        for dto_id in pe.dto_ids or []:
            mapping = self._mappings.setdefault(dto_id, EntityMapping())
            mapping.skipped_order_indices.add(0)

    def _mark_invoice_skipped(self, pe: PendingEntity) -> None:
        for dto_id in pe.dto_ids or []:
            mapping = self._mappings.setdefault(dto_id, EntityMapping())
            mapping.skipped_invoice_indices.add(0)


def build_entity_mappings(
    pending_entities: list[PendingEntity],
) -> dict[UUID, EntityMapping]:
    return EntityMappingBuilder(pending_entities).build()
