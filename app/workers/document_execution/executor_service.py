from decimal import Decimal
from typing import Any
from uuid import UUID

from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.ai.documents.pending_document import PendingDocument
from commons.db.v6.ai.entities.enums import ConfirmationStatus, EntityPendingType
from commons.db.v6.ai.entities.pending_entity import PendingEntity
from commons.dtos import OrderDTO
from commons.dtos.common.base_entity_dto import BaseDTOModel
from commons.dtos.common.dto_loader_service import DTOLoaderService
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.workers.document_execution.converters.order_converter import OrderConverter

from .converters.base import BaseEntityConverter
from .converters.entity_mapping import EntityMapping

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

        entity_mappings = self._build_entity_mappings(pending_document.pending_entities)
        logger.info(f"Built entity mapping: {entity_mappings}")

        converter = self.get_converter(pending_document.entity_type)
        dtos = await self._parse_dtos(converter, pending_document)
        logger.info(f"Parsed {len(dtos)} DTOs from extracted_data_json")

        created_ids: list[UUID] = []

        for i, dto in enumerate(dtos):
            logger.info(f"Processing DTO {i + 1}/{len(dtos)}")
            entity_mapping = entity_mappings.get(dto.id, EntityMapping())
            entity_id = await self._create_entity(
                converter=converter,
                dto=dto,
                entity_mapping=entity_mapping,
            )
            created_ids.append(entity_id)

        return created_ids

    def _build_entity_mappings(
        self,
        pending_entities: list[PendingEntity],
    ) -> dict[UUID, EntityMapping]:
        mappings: dict[UUID, EntityMapping] = {}

        logger.info(
            f"Building entity mapping from {len(pending_entities)} PendingEntities"
        )

        for pe in pending_entities:
            if pe.confirmation_status not in CONFIRMED_STATUSES:
                continue

            if not pe.best_match_id:
                logger.warning(
                    f"PendingEntity {pe.id} is confirmed but has no best_match_id"
                )
                continue

            mapping = EntityMapping()

            match pe.entity_type:
                case EntityPendingType.FACTORIES:
                    mapping.factory_id = pe.best_match_id
                case EntityPendingType.CUSTOMERS:
                    mapping.sold_to_customer_id = pe.best_match_id
                case EntityPendingType.BILL_TO_CUSTOMERS:
                    mapping.bill_to_customer_id = pe.best_match_id
                case EntityPendingType.PRODUCTS:
                    if pe.flow_index_detail is not None:
                        mapping.products[pe.flow_index_detail] = pe.best_match_id
                case EntityPendingType.END_USERS:
                    if pe.flow_index_detail is not None:
                        mapping.end_users[pe.flow_index_detail] = pe.best_match_id

            for dto_id in pe.dto_ids or []:
                existing_mapping = mappings.get(dto_id)
                if existing_mapping:
                    if mapping.factory_id:
                        existing_mapping.factory_id = mapping.factory_id
                    if mapping.sold_to_customer_id:
                        existing_mapping.sold_to_customer_id = (
                            mapping.sold_to_customer_id
                        )
                    if mapping.bill_to_customer_id:
                        existing_mapping.bill_to_customer_id = (
                            mapping.bill_to_customer_id
                        )
                    existing_mapping.products.update(mapping.products)
                    existing_mapping.end_users.update(mapping.end_users)

                else:
                    mappings[dto_id] = mapping

        return mappings

    async def _parse_dtos(
        self, converter: BaseEntityConverter, pending_document: PendingDocument
    ) -> list[BaseDTOModel]:
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
        entity_mapping: EntityMapping,
    ) -> UUID:
        input_obj = await converter.to_input(dto, entity_mapping)
        entity = await converter.create_entity(input_obj)
        return entity.id

    @staticmethod
    def _calc_rate(numerator: Decimal, denominator: Decimal) -> Decimal:
        if denominator == 0:
            return Decimal("0")
        return (numerator / denominator) * Decimal("100")
