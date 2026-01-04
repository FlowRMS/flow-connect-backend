from decimal import Decimal
from typing import Any
from uuid import UUID

from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.ai.documents.pending_document import PendingDocument
from commons.db.v6.ai.entities.enums import ConfirmationStatus, EntityPendingType
from commons.db.v6.ai.entities.pending_entity import PendingEntity
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.order.order_dto import OrderDTO
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.workers.document_execution.converters.order_converter import OrderConverter

from .converters.base import BaseEntityConverter

CONFIRMED_STATUSES = frozenset(
    {
        ConfirmationStatus.CONFIRMED,
        ConfirmationStatus.AUTO_MATCHED,
        ConfirmationStatus.CREATED_NEW,
    }
)


class DocumentExecutorService:
    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        order_converter: OrderConverter,
    ) -> None:
        super().__init__()
        self.session = session
        self.dto_loader_service = dto_loader_service
        self.order_converter = order_converter

    def get_converter(
        self,
        entity_type: DocumentEntityType,
    ) -> BaseEntityConverter[Any, Any, Any]:
        match entity_type:
            case DocumentEntityType.ORDERS:
                return self.order_converter
            case _:
                raise ValueError(f"Unsupported entity type: {entity_type}")

    async def execute(self, pending_document_id: UUID) -> list[UUID]:
        pending_document = await self.session.get_one(
            PendingDocument,
            pending_document_id,
            options=[joinedload(PendingDocument.pending_entities)],
        )
        if not pending_document.entity_type:
            raise ValueError("PendingDocument has no entity_type set")

        entity_mapping = self._build_entity_mapping(pending_document.pending_entities)
        logger.info(f"Built entity mapping with {len(entity_mapping)} entries")

        converter = self.get_converter(pending_document.entity_type)
        dtos = await self._parse_dtos(converter, pending_document)
        logger.info(f"Parsed {len(dtos)} DTOs from extracted_data_json")

        created_ids: list[UUID] = []

        for i, dto in enumerate(dtos):
            logger.info(f"Processing DTO {i + 1}/{len(dtos)}")
            entity_id = await self._create_entity(
                converter=converter,
                dto=dto,
                entity_mapping=entity_mapping,
            )
            created_ids.append(entity_id)

        return created_ids

    def _build_entity_mapping(
        self,
        pending_entities: list[PendingEntity],
    ) -> dict[str, UUID]:
        mapping: dict[str, UUID] = {}

        logger.info(
            f"Building entity mapping from {len(pending_entities)} PendingEntities"
        )

        for pe in pending_entities:
            print(
                f"Processing PendingEntity {pe.id} of type {pe.entity_type}, status {pe.confirmation_status}"
            )
            if pe.confirmation_status not in CONFIRMED_STATUSES:
                continue

            if not pe.best_match_id:
                logger.warning(
                    f"PendingEntity {pe.id} is confirmed but has no best_match_id"
                )
                continue

            match pe.entity_type:
                case EntityPendingType.FACTORIES:
                    mapping["factory"] = pe.best_match_id
                case EntityPendingType.CUSTOMERS:
                    mapping["sold_to_customer"] = pe.best_match_id
                case EntityPendingType.BILL_TO_CUSTOMERS:
                    mapping["bill_to_customer"] = pe.best_match_id
                case EntityPendingType.PRODUCTS:
                    key = f"product_{pe.flow_index_detail}"
                    mapping[key] = pe.best_match_id
                case EntityPendingType.END_USERS:
                    key = f"end_user_{pe.flow_index_detail}"
                    mapping[key] = pe.best_match_id

        return mapping

    async def _parse_dtos(
        self, converter: BaseEntityConverter, pending_document: PendingDocument
    ) -> list[Any]:
        if not pending_document.extracted_data_json:
            return []

        loaded_dtos = await converter.parse_dtos_from_json(pending_document)

        match pending_document.entity_type:
            case DocumentEntityType.ORDERS:
                return [OrderDTO.model_validate(d) for d in loaded_dtos.dtos]
            case _:
                raise ValueError(
                    f"Unsupported entity type: {pending_document.entity_type}"
                )

    async def _create_entity(
        self,
        converter: BaseEntityConverter[Any, Any, Any],
        dto: Any,
        entity_mapping: dict[str, UUID],
    ) -> UUID:
        input_obj = await converter.to_input(dto, entity_mapping)
        return await converter.create_entity(input_obj)

    @staticmethod
    def _calc_rate(numerator: Decimal, denominator: Decimal) -> Decimal:
        if denominator == 0:
            return Decimal("0")
        return (numerator / denominator) * Decimal("100")
