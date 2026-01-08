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


class DocumentBatchProcessor:
    async def execute_bulk(
        self,
        converter: BaseEntityConverter[Any, Any, Any],
        dtos: list[Any],
        entity_mappings: dict[UUID, EntityMapping],
        pending_document: PendingDocument,
        batch_size: int,
        link_callback: Any,
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

            batch_dtos, batch_mappings = converter.deduplicate(
                batch_dtos, batch_mappings
            )

            batch_records = await self._process_batch(
                converter=converter,
                dtos=batch_dtos,
                mappings=batch_mappings,
                pending_document=pending_document,
                link_callback=link_callback,
            )
            processing_records.extend(batch_records)

        return processing_records

    async def _process_batch(
        self,
        converter: BaseEntityConverter[Any, Any, Any],
        dtos: list[Any],
        mappings: list[EntityMapping],
        pending_document: PendingDocument,
        link_callback: Any,
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
                logger.error(f"Error converting DTO {i}: {e}")
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
                            error_message="Duplicate or could not be created",
                        )
                    )
                else:
                    entity = bulk_result.created[created_idx]
                    created_idx += 1
                    await link_callback(pending_document, entity.id)
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
