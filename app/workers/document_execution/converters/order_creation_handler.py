from uuid import UUID

from commons.db.v6.ai.entities.enums import ConfirmationStatus, EntityPendingType
from commons.db.v6.ai.entities.pending_entity import PendingEntity
from commons.dtos.order.order_dto import OrderDTO
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from .creation_types import CreationIssue, CreationResult
from .dto_grouper import group_order_dtos
from .entity_mapping import EntityMapping
from .order_converter import OrderConverter


class OrderCreationHandler:
    def __init__(
        self,
        session: AsyncSession,
        order_converter: OrderConverter,
    ) -> None:
        super().__init__()
        self._session = session
        self._order_converter = order_converter

    async def create_orders(
        self,
        pending_entities: list[PendingEntity],
        entity_mappings: dict[UUID, EntityMapping],
        result: CreationResult,
    ) -> int:
        order_entities = [
            pe
            for pe in pending_entities
            if pe.confirmation_status == ConfirmationStatus.SET_FOR_CREATION
            and pe.entity_type == EntityPendingType.ORDERS
        ]

        if not order_entities:
            return 0

        grouped_orders = group_order_dtos(order_entities, entity_mappings)
        if not grouped_orders:
            return 0

        dtos: list[OrderDTO] = []
        mappings: list[EntityMapping] = []

        for grouped in grouped_orders:
            if not grouped.dto_ids:
                continue
            first_dto_id = grouped.dto_ids[0]
            mapping = entity_mappings.get(first_dto_id, EntityMapping())
            dtos.append(grouped.dto)
            mappings.append(mapping)

        if not dtos:
            return 0

        inputs = await self._order_converter.to_inputs_bulk(dtos, mappings)
        if not inputs:
            return 0

        created_count = 0
        for i, (inp, grouped) in enumerate(zip(inputs, grouped_orders, strict=False)):
            pe_id = grouped.pending_entities[0].id if grouped.pending_entities else None
            async with self._session.begin_nested():
                try:
                    order = await self._order_converter.create_entity(inp)
                    for pe in grouped.pending_entities:
                        self._update_mappings(entity_mappings, pe, order.id)
                    logger.info(
                        f"Created order {order.id} with {len(grouped.dto.details)} "
                        f"details (grouped from {len(grouped.pending_entities)} records)"
                    )
                    created_count += 1
                except Exception as e:
                    logger.exception(f"Failed to create order at index {i}: {e}")
                    result.issues.append(
                        CreationIssue(
                            entity_type=EntityPendingType.ORDERS,
                            pending_entity_id=pe_id,
                            error_message=str(e),
                            dto_json=grouped.dto.model_dump(mode="json"),
                        )
                    )

        return created_count

    def _update_mappings(
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
