from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from uuid import UUID

TDto = TypeVar("TDto")
TInput = TypeVar("TInput")


class BaseEntityConverter(ABC, Generic[TDto, TInput]):
    @abstractmethod
    def to_input(
        self,
        dto: TDto,
        entity_mapping: dict[str, UUID],
    ) -> TInput:
        """
        Convert a DTO from commons to a Strawberry input using confirmed entity IDs.

        Args:
            dto: The extracted DTO from PendingDocument.extracted_data_json
            entity_mapping: Map of entity keys to confirmed UUIDs
                - "factory": Factory UUID
                - "sold_to_customer": Sold-to customer UUID
                - "bill_to_customer": Bill-to customer UUID (optional)
                - "product_{index}": Product UUID for line item at index
                - "end_user_{index}": End user UUID for line item at index

        Returns:
            Strawberry input ready for service creation
        """
        ...

    @staticmethod
    def parse_dtos_from_json(extracted_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Parse raw DTOs from PendingDocument.extracted_data_json.

        For PDFs: {"data": [{"order_number": "...", ...}]}
        For Tabular: {"s3_key": "..."} - needs separate handling
        """
        if "data" in extracted_data:
            return extracted_data["data"]
        return []
