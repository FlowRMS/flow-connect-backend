from dataclasses import dataclass
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
from loguru import logger

from .converters.base import BaseEntityConverter
from .converters.entity_mapping import EntityMapping
from .converters.skipped_entity_handler import (
    is_dto_skipped_for_invoice,
    is_dto_skipped_for_order,
)


@dataclass
class BatchProcessingResult:
    records: list[PendingDocumentProcessing]
    created_count: int
    updated_count: int
    skipped_count: int
    error_count: int


class DocumentBatchProcessor:
    async def execute_bulk(
        self,
        converter: BaseEntityConverter[Any, Any, Any],
        dtos: list[Any],
        entity_mappings: dict[UUID, EntityMapping],
        pending_document: PendingDocument,
        batch_size: int,
    ) -> list[PendingDocumentProcessing]:
        processing_records: list[PendingDocumentProcessing] = []

        fallback_mapping = self._get_fallback_mapping(entity_mappings)
        for batch_start in range(0, len(dtos), batch_size):
            batch_end = min(batch_start + batch_size, len(dtos))
            batch_dtos = dtos[batch_start:batch_end]
            logger.info(
                f"Processing batch {batch_start + 1}-{batch_end} of {len(dtos)} DTOs"
            )

            batch_mappings = [
                entity_mappings.get(dto.internal_uuid) or fallback_mapping
                for dto in batch_dtos
            ]

            batch_dtos, batch_mappings = converter.deduplicate(
                batch_dtos, batch_mappings
            )

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
        user_skipped_indices: set[int] = set()

        for i, (dto, mapping) in enumerate(zip(dtos, mappings, strict=True)):
            if self._is_dto_skipped(mapping, pending_document.entity_type):
                user_skipped_indices.add(i)
                continue

            try:
                result = await converter.to_input(dto, mapping)
                if result.is_error():
                    conversion_errors[i] = str(result.unwrap_error())
                    continue

                if result.value is None:
                    conversion_errors[i] = (
                        "Record could not be converted to input. Missing required fields?"
                    )
                    continue

                valid_inputs.append(result.unwrap())
                valid_indices.append(i)
            except Exception as e:
                logger.exception(f"Error converting DTO {i}: {e}")
                conversion_errors[i] = str(e)

        for i in user_skipped_indices:
            records.append(
                PendingDocumentProcessing(
                    pending_document_id=pending_document.id,
                    entity_id=None,
                    status=ProcessingResultStatus.SKIPPED,
                    dto_json=dtos[i].model_dump(mode="json"),
                    error_message="Skipped by user",
                )
            )

        if valid_inputs:
            separated = await converter.separate_inputs(valid_inputs)

            create_result = await converter.create_entities_bulk(separated.for_creation)
            update_result = await converter.update_entities_bulk(separated.for_update)

            create_skipped_set = set(create_result.skipped_indices)
            update_skipped_set = set(update_result.skipped_indices)

            created_idx = 0
            updated_idx = 0

            for list_pos, original_idx in enumerate(valid_indices):
                dto = dtos[original_idx]

                if list_pos in separated.for_creation_indices:
                    create_pos = separated.for_creation_indices.index(list_pos)
                    if create_pos in create_skipped_set:
                        records.append(
                            PendingDocumentProcessing(
                                pending_document_id=pending_document.id,
                                entity_id=None,
                                status=ProcessingResultStatus.SKIPPED,
                                dto_json=dto.model_dump(mode="json"),
                                error_message="Duplicate or could not be created",
                            )
                        )
                    else:
                        entity = create_result.created[created_idx]
                        created_idx += 1
                        records.append(
                            PendingDocumentProcessing(
                                pending_document_id=pending_document.id,
                                entity_id=entity.id,
                                status=ProcessingResultStatus.CREATED,
                                dto_json=dto.model_dump(mode="json"),
                                error_message=None,
                            )
                        )

                elif list_pos in separated.for_update_indices:
                    update_pos = separated.for_update_indices.index(list_pos)
                    if update_pos in update_skipped_set:
                        records.append(
                            PendingDocumentProcessing(
                                pending_document_id=pending_document.id,
                                entity_id=None,
                                status=ProcessingResultStatus.SKIPPED,
                                dto_json=dto.model_dump(mode="json"),
                                error_message="Could not be updated",
                            )
                        )
                    else:
                        entity = update_result.created[updated_idx]
                        updated_idx += 1
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

    @staticmethod
    def _get_fallback_mapping(
        entity_mappings: dict[UUID, EntityMapping],
    ) -> EntityMapping:
        fallback = EntityMapping()
        for mapping in entity_mappings.values():
            if mapping.factory_id and not fallback.factory_id:
                fallback.factory_id = mapping.factory_id
            if mapping.sold_to_customer_id and not fallback.sold_to_customer_id:
                fallback.sold_to_customer_id = mapping.sold_to_customer_id
            if mapping.bill_to_customer_id and not fallback.bill_to_customer_id:
                fallback.bill_to_customer_id = mapping.bill_to_customer_id
            fallback.products.update(mapping.products)
            fallback.end_users.update(mapping.end_users)
            if mapping.default_end_user_id and not fallback.default_end_user_id:
                fallback.default_end_user_id = mapping.default_end_user_id
            fallback.orders.update(mapping.orders)
            fallback.invoices.update(mapping.invoices)
            fallback.credits.update(mapping.credits)
            fallback.adjustments.update(mapping.adjustments)
            fallback.sold_to_customer_ids.update(mapping.sold_to_customer_ids)
            fallback.skipped_product_indices.update(mapping.skipped_product_indices)
            fallback.skipped_order_indices.update(mapping.skipped_order_indices)
            fallback.skipped_invoice_indices.update(mapping.skipped_invoice_indices)
        return fallback

    @staticmethod
    def _is_dto_skipped(
        mapping: EntityMapping,
        entity_type: DocumentEntityType | None,
    ) -> bool:
        match entity_type:
            case DocumentEntityType.ORDERS:
                return is_dto_skipped_for_order(mapping)
            case DocumentEntityType.INVOICES:
                return is_dto_skipped_for_invoice(mapping)
            case _:
                return False
