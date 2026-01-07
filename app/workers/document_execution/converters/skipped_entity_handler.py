from typing import TypeVar

from commons.dtos.common.base_entity_dto import BaseEntityDTO
from commons.dtos.common.base_part_number_dto import BasePartNumberDTO

from .entity_mapping import EntityMapping

TDetail = TypeVar("TDetail", bound=BasePartNumberDTO)
TDto = TypeVar("TDto", bound=BaseEntityDTO)


def filter_skipped_details(
    dto: BaseEntityDTO[TDetail],
    entity_mapping: EntityMapping,
) -> list[TDetail]:
    if not entity_mapping.skipped_product_indices:
        return list(dto.details)

    return [
        detail
        for detail in dto.details
        if detail.flow_index not in entity_mapping.skipped_product_indices
    ]


def is_dto_skipped_for_order(entity_mapping: EntityMapping) -> bool:
    return bool(entity_mapping.skipped_order_indices)


def is_dto_skipped_for_invoice(entity_mapping: EntityMapping) -> bool:
    return bool(entity_mapping.skipped_invoice_indices)
