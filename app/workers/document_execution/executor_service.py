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
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.enums import WorkflowStatus
from commons.dtos.common.dto_loader_service import DTOLoaderService
from loguru import logger
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.db.transient_session import TransientSession
from app.graphql.links.services.links_service import LinksService
from app.workers.document_execution.converters.check_converter import CheckConverter
from app.workers.document_execution.converters.customer_converter import (
    CustomerConverter,
)
from app.workers.document_execution.converters.entity_mapping_builder import (
    build_entity_mappings,
)
from app.workers.document_execution.converters.factory_converter import FactoryConverter
from app.workers.document_execution.converters.invoice_converter import InvoiceConverter
from app.workers.document_execution.converters.order_ack_converter import (
    OrderAckConverter,
)
from app.workers.document_execution.converters.order_converter import OrderConverter
from app.workers.document_execution.converters.product_converter import ProductConverter
from app.workers.document_execution.converters.quote_converter import QuoteConverter
from app.workers.document_execution.converters.set_for_creation_service import (
    SetForCreationService,
)

from .batch_processor import DocumentBatchProcessor
from .converters.base import DEFAULT_BATCH_SIZE, BaseEntityConverter

DOCUMENT_TO_LINK_ENTITY_TYPE: dict[DocumentEntityType, EntityType] = {
    DocumentEntityType.QUOTES: EntityType.QUOTE,
    DocumentEntityType.ORDERS: EntityType.ORDER,
    DocumentEntityType.INVOICES: EntityType.INVOICE,
    DocumentEntityType.CHECKS: EntityType.CHECK,
    DocumentEntityType.CUSTOMERS: EntityType.CUSTOMER,
    DocumentEntityType.FACTORIES: EntityType.FACTORY,
    DocumentEntityType.PRODUCTS: EntityType.PRODUCT,
    DocumentEntityType.ORDER_ACKNOWLEDGEMENTS: EntityType.ORDER_ACKNOWLEDGEMENT,
}


class DocumentExecutorService:
    def __init__(
        self,
        session: AsyncSession,
        transient_session: TransientSession,
        dto_loader_service: DTOLoaderService,
        links_service: LinksService,
        quote_converter: QuoteConverter,
        order_converter: OrderConverter,
        customer_converter: CustomerConverter,
        factory_converter: FactoryConverter,
        product_converter: ProductConverter,
        invoice_converter: InvoiceConverter,
        check_converter: CheckConverter,
        order_ack_converter: OrderAckConverter,
        set_for_creation_service: SetForCreationService,
    ) -> None:
        super().__init__()
        self.session = session
        self.transient_session = transient_session
        self.dto_loader_service = dto_loader_service
        self.links_service = links_service
        self.quote_converter = quote_converter
        self.order_converter = order_converter
        self.customer_converter = customer_converter
        self.factory_converter = factory_converter
        self.product_converter = product_converter
        self.invoice_converter = invoice_converter
        self.check_converter = check_converter
        self.order_ack_converter = order_ack_converter
        self.set_for_creation_service = set_for_creation_service
        self._batch_processor = DocumentBatchProcessor()

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
            case DocumentEntityType.CHECKS:
                return self.check_converter
            case DocumentEntityType.ORDER_ACKNOWLEDGEMENTS:
                return self.order_ack_converter
            case _:
                raise ValueError(f"Unsupported entity type: {entity_type}")

    async def execute(
        self,
        pending_document_id: UUID,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> list[PendingDocumentProcessing]:
        pending_document = await self.transient_session.get_one(
            PendingDocument,
            pending_document_id,
            options=[joinedload(PendingDocument.pending_entities)],
        )
        try:
            if not pending_document.entity_type:
                raise ValueError("PendingDocument has no entity_type set")

            entity_mappings = build_entity_mappings(pending_document.pending_entities)
            logger.info(f"Built entity mapping: {entity_mappings}")

            converter = self.get_converter(pending_document.entity_type)
            logger.info(
                f"Using converter {converter.__class__.__name__} for entity type {pending_document.entity_type.name}"
            )
            dtos = await self._parse_dtos(converter, pending_document)
            logger.info(f"Parsed {len(dtos)} DTOs from extracted_data_json")

            creation_result = (
                await self.set_for_creation_service.process_set_for_creation(
                    pending_entities=pending_document.pending_entities,
                    entity_mappings=entity_mappings,
                )
            )
            processing_records: list[PendingDocumentProcessing] = []
            if creation_result.has_issues:
                for issue in creation_result.issues:
                    error = issue.error_message
                    processing_records.append(
                        PendingDocumentProcessing(
                            pending_document_id=pending_document.id,
                            entity_id=None,
                            status=ProcessingResultStatus.ERROR,
                            dto_json=issue.dto_json,
                            error_message=error,
                        )
                    )
                pending_document.workflow_status = WorkflowStatus.FAILED
            else:
                logger.info(
                    f"SET_FOR_CREATION completed: orders={creation_result.orders_created}, "
                    f"invoices={creation_result.invoices_created}, "
                    f"credits={creation_result.credits_created}, "
                    f"adjustments={creation_result.adjustments_created}"
                )

                processing_records = await self._batch_processor.execute_bulk(
                    converter=converter,
                    dtos=dtos,
                    entity_mappings=entity_mappings,
                    pending_document=pending_document,
                    batch_size=batch_size,
                )
                created_entity_ids = [
                    r.entity_id for r in processing_records if r.entity_id is not None
                ]
                await self._link_file_to_entities(pending_document, created_entity_ids)
                pending_document.workflow_status = WorkflowStatus.COMPLETED

            self.session.add_all(processing_records)
            await self.session.flush()

            return processing_records
        except Exception as e:
            _ = await self.transient_session.execute(
                update(PendingDocument)
                .where(PendingDocument.id == pending_document_id)
                .values(workflow_status=WorkflowStatus.FAILED)
            )
            await self.transient_session.flush()
            logger.exception(f"Error executing document {pending_document_id}: {e}")
            return []

    async def _parse_dtos(
        self,
        converter: BaseEntityConverter[Any, Any, Any],
        pending_document: PendingDocument,
    ) -> list[Any]:
        if not pending_document.extracted_data_json:
            return []

        loaded_dtos = await converter.parse_dtos_from_json(pending_document)
        return [converter.dto_class.model_validate(d) for d in loaded_dtos.dtos]

    async def _link_file_to_entities(
        self,
        pending_document: PendingDocument,
        entity_ids: list[UUID],
    ) -> None:
        if not entity_ids or not pending_document.entity_type:
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
            links = await self.links_service.bulk_create_links(
                source_type=EntityType.FILE,
                source_id=pending_document.file_id,
                target_type=link_entity_type,
                target_ids=entity_ids,
            )
            logger.info(
                f"Linked file {pending_document.file_id} to {len(links)} {link_entity_type.name} entities"
            )
        except Exception as e:
            logger.warning(f"Failed to bulk link file to entities: {e}")
