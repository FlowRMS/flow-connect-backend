from decimal import Decimal
from typing import Any
from uuid import UUID

import strawberry
from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.ai.documents.pending_document import PendingDocument
from commons.db.v6.ai.entities.enums import ConfirmationStatus, EntityPendingType
from commons.db.v6.ai.entities.pending_entity import PendingEntity
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.enums import WorkflowStatus
from commons.dtos.common.dto_loader_service import DTOLoaderService
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.graphql.links.services.links_service import LinksService
from app.workers.document_execution.converters.customer_converter import (
    CustomerConverter,
)
from app.workers.document_execution.converters.factory_converter import FactoryConverter
from app.workers.document_execution.converters.invoice_converter import InvoiceConverter
from app.workers.document_execution.converters.order_converter import OrderConverter
from app.workers.document_execution.converters.product_converter import ProductConverter
from app.workers.document_execution.converters.quote_converter import QuoteConverter

from .converters.base import BaseEntityConverter
from .converters.entity_mapping import EntityMapping


@strawberry.type
class EntityProcessResponse:
    entity_id: UUID | None
    dto: strawberry.scalars.JSON
    error: str | None


CONFIRMED_STATUSES = frozenset(
    {
        ConfirmationStatus.CONFIRMED,
        ConfirmationStatus.AUTO_MATCHED,
        ConfirmationStatus.CREATED_NEW,
    }
)

DOCUMENT_TO_LINK_ENTITY_TYPE: dict[DocumentEntityType, EntityType] = {
    DocumentEntityType.ORDERS: EntityType.ORDER,
    DocumentEntityType.CUSTOMERS: EntityType.CUSTOMER,
    DocumentEntityType.FACTORIES: EntityType.FACTORY,
    DocumentEntityType.PRODUCTS: EntityType.PRODUCT,
    DocumentEntityType.INVOICES: EntityType.INVOICE,
}


class DocumentExecutorService:
    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        links_service: LinksService,
        quote_converter: QuoteConverter,
        order_converter: OrderConverter,
        customer_converter: CustomerConverter,
        factory_converter: FactoryConverter,
        product_converter: ProductConverter,
        invoice_converter: InvoiceConverter,
    ) -> None:
        super().__init__()
        self.session = session
        self.dto_loader_service = dto_loader_service
        self.links_service = links_service
        self.quote_converter = quote_converter
        self.order_converter = order_converter
        self.customer_converter = customer_converter
        self.factory_converter = factory_converter
        self.product_converter = product_converter
        self.invoice_converter = invoice_converter

    def get_converter(
        self,
        entity_type: DocumentEntityType,
    ) -> BaseEntityConverter[Any, Any, Any]:
        match entity_type:
            case DocumentEntityType.QUOTES:
                return self.quote_converter
            case DocumentEntityType.ORDERS:
                return self.order_converter
            case DocumentEntityType.CUSTOMERS:
                return self.customer_converter
            case DocumentEntityType.FACTORIES:
                return self.factory_converter
            case DocumentEntityType.PRODUCTS:
                return self.product_converter
            case DocumentEntityType.INVOICES:
                return self.invoice_converter
            case _:
                raise ValueError(f"Unsupported entity type: {entity_type}")

    async def execute(self, pending_document_id: UUID) -> list[EntityProcessResponse]:
        pending_document = await self.session.get_one(
            PendingDocument,
            pending_document_id,
            options=[joinedload(PendingDocument.pending_entities)],
        )
        try:
            if not pending_document.entity_type:
                raise ValueError("PendingDocument has no entity_type set")

            entity_mappings = self._build_entity_mappings(
                pending_document.pending_entities
            )
            logger.info(f"Built entity mapping: {entity_mappings}")

            converter = self.get_converter(pending_document.entity_type)
            dtos = await self._parse_dtos(converter, pending_document)
            logger.info(f"Parsed {len(dtos)} DTOs from extracted_data_json")

            created_responses: list[EntityProcessResponse] = []

            for i, dto in enumerate(dtos):
                logger.info(
                    f"Processing DTO {i + 1}/{len(dtos)} dto.id={dto.internal_uuid}"
                )
                # dto_id = getattr(dto, "id", None)
                # if dto_id:
                entity_mapping = entity_mappings.get(dto.internal_uuid, EntityMapping())
                # else:
                # entity_mapping = EntityMapping()
                entity_response = await self._create_entity(
                    converter=converter,
                    dto=dto,
                    entity_mapping=entity_mapping,
                    pending_document=pending_document,
                )
                created_responses.append(entity_response)

            pending_document.workflow_status = WorkflowStatus.COMPLETED
            return created_responses
        except Exception as e:
            pending_document.workflow_status = WorkflowStatus.FAILED
            logger.exception(f"Error executing document {pending_document_id}: {e}")
            raise

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
                case EntityPendingType.ORDERS:
                    mapping.order_id = pe.best_match_id
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
                    if mapping.order_id:
                        existing_mapping.order_id = mapping.order_id
                    existing_mapping.products.update(mapping.products)
                    existing_mapping.end_users.update(mapping.end_users)

                else:
                    mappings[dto_id] = mapping

        return mappings

    async def _parse_dtos(
        self,
        converter: BaseEntityConverter[Any, Any, Any],
        pending_document: PendingDocument,
    ) -> list[Any]:
        if not pending_document.extracted_data_json:
            return []

        loaded_dtos = await converter.parse_dtos_from_json(pending_document)
        return [converter.dto_class.model_validate(d) for d in loaded_dtos.dtos]

    async def _create_entity(
        self,
        converter: BaseEntityConverter[Any, Any, Any],
        dto: BaseModel,
        entity_mapping: EntityMapping,
        pending_document: PendingDocument,
    ) -> EntityProcessResponse:
        try:
            input_obj = await converter.to_input(dto, entity_mapping)
            entity = await converter.create_entity(input_obj)
            await self._link_file_to_entity(pending_document, entity.id)
            return EntityProcessResponse(
                entity_id=entity.id,
                dto=dto.model_dump(),
                error=None,
            )
        except Exception as e:
            logger.error(f"Error creating entity for DTO: {e}")
            return EntityProcessResponse(
                entity_id=None,
                dto=dto.model_dump(),
                error=str(e),
            )

    async def _link_file_to_entity(
        self,
        pending_document: PendingDocument,
        entity_id: UUID,
    ) -> None:
        if not pending_document.entity_type:
            return

        link_entity_type = DOCUMENT_TO_LINK_ENTITY_TYPE.get(
            pending_document.entity_type
        )
        if not link_entity_type:
            logger.warning(
                f"No link entity type mapping for {pending_document.entity_type}"
            )
            return

        try:
            _ = await self.links_service.create_link(
                source_type=EntityType.FILE,
                source_id=pending_document.file_id,
                target_type=link_entity_type,
                target_id=entity_id,
            )
            logger.info(
                f"Linked file {pending_document.file_id} to {link_entity_type.name} {entity_id}"
            )
        except Exception as e:
            logger.warning(f"Failed to link file to entity: {e}")

    @staticmethod
    def _calc_rate(numerator: Decimal, denominator: Decimal) -> Decimal:
        if denominator == 0:
            return Decimal("0")
        return (numerator / denominator) * Decimal("100")
