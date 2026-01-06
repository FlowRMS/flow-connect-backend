from decimal import Decimal
from typing import Any
from uuid import UUID

from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.db.v6.ai.documents.enums.processing_result_status import (
    ProcessingResultStatus,
)
from commons.db.v6.ai.documents.pending_document import PendingDocument
from commons.db.v6.ai.documents.pending_document_processing import (
    PendingDocumentProcessing,
)
from commons.db.v6.ai.entities.enums import ConfirmationStatus, EntityPendingType
from commons.db.v6.ai.entities.pending_entity import PendingEntity
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.enums import WorkflowStatus
from commons.dtos.common.dto_loader_service import DTOLoaderService
from loguru import logger
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

from .converters.base import DEFAULT_BATCH_SIZE, BaseEntityConverter
from .converters.entity_mapping import EntityMapping

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

    async def execute(
        self,
        pending_document_id: UUID,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> list[PendingDocumentProcessing]:
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

            processing_records = await self._execute_bulk(
                converter=converter,
                dtos=dtos,
                entity_mappings=entity_mappings,
                pending_document=pending_document,
                batch_size=batch_size,
            )

            self.session.add_all(processing_records)
            await self.session.flush()

            pending_document.workflow_status = WorkflowStatus.COMPLETED
            return processing_records
        except Exception as e:
            pending_document.workflow_status = WorkflowStatus.FAILED
            logger.exception(f"Error executing document {pending_document_id}: {e}")
            raise

    async def _execute_bulk(
        self,
        converter: BaseEntityConverter[Any, Any, Any],
        dtos: list[Any],
        entity_mappings: dict[UUID, EntityMapping],
        pending_document: PendingDocument,
        batch_size: int,
    ) -> list[PendingDocumentProcessing]:
        processing_records: list[PendingDocumentProcessing] = []

        for batch_start in range(0, len(dtos), batch_size):
            batch_end = min(batch_start + batch_size, len(dtos))
            batch_dtos = dtos[batch_start:batch_end]
            logger.info(
                f"Processing batch {batch_start + 1}-{batch_end} of {len(dtos)} DTOs"
            )

            batch_mappings = [
                entity_mappings.get(dto.internal_uuid, EntityMapping())
                for dto in batch_dtos
            ]

            batch_records = await self._process_batch(
                converter=converter,
                dtos=batch_dtos,
                mappings=batch_mappings,
                pending_document=pending_document,
            )
            processing_records.extend(batch_records)

        return processing_records

    async def _process_batch(
        self,
        converter: BaseEntityConverter[Any, Any, Any],
        dtos: list[Any],
        mappings: list[EntityMapping],
        pending_document: PendingDocument,
    ) -> list[PendingDocumentProcessing]:
        records: list[PendingDocumentProcessing] = []
        conversion_errors: dict[int, str] = {}
        valid_inputs: list[Any] = []
        valid_indices: list[int] = []

        for i, (dto, mapping) in enumerate(zip(dtos, mappings, strict=True)):
            try:
                inp = await converter.to_input(dto, mapping)
                valid_inputs.append(inp)
                valid_indices.append(i)
            except Exception as e:
                logger.error(f"Error converting DTO {i}: {e}")
                conversion_errors[i] = str(e)

        if valid_inputs:
            bulk_result = await converter.create_entities_bulk(valid_inputs)

            skipped_set = set(bulk_result.skipped_indices)
            created_idx = 0
            for list_pos, original_idx in enumerate(valid_indices):
                dto = dtos[original_idx]
                if list_pos in skipped_set:
                    records.append(
                        PendingDocumentProcessing(
                            pending_document_id=pending_document.id,
                            entity_id=None,
                            status=ProcessingResultStatus.SKIPPED,
                            dto_json=dto.model_dump(mode="json"),
                            error_message="Skipped: duplicate or validation error",
                        )
                    )
                else:
                    entity = bulk_result.created[created_idx]
                    created_idx += 1
                    await self._link_file_to_entity(pending_document, entity.id)
                    records.append(
                        PendingDocumentProcessing(
                            pending_document_id=pending_document.id,
                            entity_id=entity.id,
                            status=ProcessingResultStatus.CREATED,
                            dto_json=dto.model_dump(mode="json"),
                            error_message=None,
                        )
                    )

        for i, error in conversion_errors.items():
            records.append(
                PendingDocumentProcessing(
                    pending_document_id=pending_document.id,
                    entity_id=None,
                    status=ProcessingResultStatus.ERROR,
                    dto_json=dtos[i].model_dump(mode="json"),
                    error_message=error,
                )
            )

        return records

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
