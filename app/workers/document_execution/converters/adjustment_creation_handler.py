from uuid import UUID

from commons.db.v6.ai.entities.enums import ConfirmationStatus, EntityPendingType
from commons.db.v6.ai.entities.pending_entity import PendingEntity
from commons.dtos.check.check_detail_dto import CheckDetailDTO
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from .adjustment_converter import AdjustmentConverter
from .creation_types import CreationIssue, CreationResult
from .entity_mapping import EntityMapping


class AdjustmentCreationHandler:
    def __init__(
        self,
        session: AsyncSession,
        adjustment_converter: AdjustmentConverter,
    ) -> None:
        super().__init__()
        self._session = session
        self._adjustment_converter = adjustment_converter

    async def create_adjustments(
        self,
        pending_entities: list[PendingEntity],
        entity_mappings: dict[UUID, EntityMapping],
        result: CreationResult,
    ) -> int:
        adjustment_entities = [
            pe
            for pe in pending_entities
            if pe.confirmation_status == ConfirmationStatus.SET_FOR_CREATION
            and pe.entity_type == EntityPendingType.ADJUSTMENTS
        ]

        created_count = 0
        for pe in adjustment_entities:
            adjustment_id = await self._create_adjustment_for_pending_entity(
                pe, entity_mappings, result
            )
            if adjustment_id:
                self._update_mappings(entity_mappings, pe, adjustment_id)
                created_count += 1

        return created_count

    async def _create_adjustment_for_pending_entity(
        self,
        pe: PendingEntity,
        entity_mappings: dict[UUID, EntityMapping],
        result: CreationResult,
    ) -> UUID | None:
        if not pe.dto_ids:
            logger.warning(f"PendingEntity {pe.id} has no dto_ids for SET_FOR_CREATION")
            return None

        dto_id = pe.dto_ids[0]
        dto = CheckDetailDTO.model_validate(pe.extracted_data)
        mapping = entity_mappings.get(dto_id, EntityMapping())

        conversion = await self._adjustment_converter.to_input(dto, mapping)
        if conversion.is_error() or conversion.value is None:
            error_msg = str(conversion.unwrap_error())
            logger.exception(f"Failed to convert adjustment: {error_msg}")
            result.issues.append(
                CreationIssue(
                    entity_type=EntityPendingType.ADJUSTMENTS,
                    pending_entity_id=pe.id,
                    error_message=error_msg,
                    dto_json=dto.model_dump(mode="json"),
                )
            )
            return None

        async with self._session.begin_nested():
            try:
                adjustment = await self._adjustment_converter.create_entity(
                    conversion.value
                )
                logger.info(f"Created adjustment {adjustment.id} for SET_FOR_CREATION")
                return adjustment.id
            except Exception as e:
                logger.exception(
                    f"Failed to create adjustment for SET_FOR_CREATION: {e}"
                )
                result.issues.append(
                    CreationIssue(
                        entity_type=EntityPendingType.ADJUSTMENTS,
                        pending_entity_id=pe.id,
                        error_message=str(e),
                        dto_json=dto.model_dump(mode="json"),
                    )
                )
                return None

    def _update_mappings(
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
