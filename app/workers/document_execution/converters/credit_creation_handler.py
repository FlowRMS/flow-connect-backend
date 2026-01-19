from uuid import UUID

from commons.db.v6.ai.entities.enums import ConfirmationStatus, EntityPendingType
from commons.db.v6.ai.entities.pending_entity import PendingEntity
from commons.dtos.check.check_detail_dto import CheckDetailDTO
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from .creation_types import CreationIssue, CreationResult
from .credit_converter import CreditConverter
from .entity_mapping import EntityMapping


class CreditCreationHandler:
    def __init__(
        self,
        session: AsyncSession,
        credit_converter: CreditConverter,
    ) -> None:
        super().__init__()
        self._session = session
        self._credit_converter = credit_converter

    async def create_credits(
        self,
        pending_entities: list[PendingEntity],
        entity_mappings: dict[UUID, EntityMapping],
        result: CreationResult,
    ) -> int:
        credit_entities = [
            pe
            for pe in pending_entities
            if pe.confirmation_status == ConfirmationStatus.SET_FOR_CREATION
            and pe.entity_type == EntityPendingType.CREDITS
        ]

        created_count = 0
        for pe in credit_entities:
            credit_id = await self._create_credit_for_pending_entity(
                pe, entity_mappings, result
            )
            if credit_id:
                self._update_mappings(entity_mappings, pe, credit_id)
                created_count += 1

        return created_count

    async def _create_credit_for_pending_entity(
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

        if not isinstance(dto, CheckDetailDTO):
            logger.warning(f"DTO {dto_id} is not a CheckDetailDTO for credit creation")
            return None

        mapping = entity_mappings.get(dto_id, EntityMapping())

        conversion = await self._credit_converter.to_input(dto, mapping)
        if conversion.is_error() or conversion.value is None:
            error_msg = str(conversion.unwrap_error())
            logger.exception(f"Failed to convert credit: {error_msg}")
            result.issues.append(
                CreationIssue(
                    entity_type=EntityPendingType.CREDITS,
                    pending_entity_id=pe.id,
                    error_message=error_msg,
                    dto_json=dto.model_dump(mode="json"),
                )
            )
            return None

        async with self._session.begin_nested():
            try:
                credit = await self._credit_converter.create_entity(conversion.value)
                logger.info(f"Created credit {credit.id} for SET_FOR_CREATION")
                return credit.id
            except Exception as e:
                logger.exception(f"Failed to create credit for SET_FOR_CREATION: {e}")
                result.issues.append(
                    CreationIssue(
                        entity_type=EntityPendingType.CREDITS,
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
