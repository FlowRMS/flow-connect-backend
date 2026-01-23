from dataclasses import dataclass
from datetime import datetime, timezone
from typing import override
from uuid import UUID

from commons.db.v6 import Delivery
from commons.db.v6.ai.documents.enums.entity_type import DocumentEntityType
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.dtos.delivery.delivery_detail_dto import DeliveryDetailDTO
from commons.dtos.delivery.delivery_dto import DeliveryDTO
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.v2.core.deliveries.services.delivery_item_service import (
    DeliveryItemService,
)
from app.graphql.v2.core.deliveries.services.delivery_service import DeliveryService
from app.graphql.v2.core.deliveries.strawberry.inputs import (
    DeliveryInput,
    DeliveryItemInput,
)

from .base import BaseEntityConverter, ConversionResult
from .entity_mapping import EntityMapping
from .exceptions import (
    DeliveryProductRequiredError,
    DeliveryVendorRequiredError,
    DeliveryWarehouseRequiredError,
)


@dataclass(frozen=True)
class DeliveryItemDraft:
    product_id: UUID
    expected_quantity: int
    received_quantity: int
    damaged_quantity: int
    discrepancy_notes: str | None


@dataclass(frozen=True)
class DeliveryCreatePayload:
    delivery_input: DeliveryInput
    item_drafts: list[DeliveryItemDraft]


class DeliveryConverter(
    BaseEntityConverter[DeliveryDTO, DeliveryCreatePayload, Delivery]
):
    entity_type = DocumentEntityType.DELIVERIES
    dto_class = DeliveryDTO

    def __init__(
        self,
        session: AsyncSession,
        dto_loader_service: DTOLoaderService,
        delivery_service: DeliveryService,
        delivery_item_service: DeliveryItemService,
    ) -> None:
        super().__init__(session, dto_loader_service)
        self.delivery_service = delivery_service
        self.delivery_item_service = delivery_item_service

    @override
    async def create_entity(self, input_data: DeliveryCreatePayload) -> Delivery:
        delivery = await self.delivery_service.create(input_data.delivery_input)

        for item in input_data.item_drafts:
            item_input = DeliveryItemInput(
                delivery_id=delivery.id,
                product_id=item.product_id,
                expected_quantity=item.expected_quantity,
                received_quantity=item.received_quantity,
                damaged_quantity=item.damaged_quantity,
                discrepancy_notes=item.discrepancy_notes,
            )
            _ = await self.delivery_item_service.create(item_input)

        return delivery

    @override
    async def to_input(
        self,
        dto: DeliveryDTO,
        entity_mapping: EntityMapping,
    ) -> ConversionResult[DeliveryCreatePayload]:
        vendor_id = entity_mapping.factory_id
        warehouse_id = dto.warehouse_id

        if not vendor_id:
            return ConversionResult.fail(DeliveryVendorRequiredError())
        if not warehouse_id:
            return ConversionResult.fail(DeliveryWarehouseRequiredError())

        delivery_input = DeliveryInput(
            po_number=dto.po_number or self._generate_po_number(),
            warehouse_id=warehouse_id,
            vendor_id=vendor_id,
            carrier_id=None,
            tracking_number=dto.tracking_number,
            expected_date=dto.expected_date,
            vendor_contact_name=dto.vendor_contact_name,
            vendor_contact_email=dto.vendor_contact_email,
            notes=dto.notes,
        )

        item_drafts: list[DeliveryItemDraft] = []
        for detail in dto.details:
            detail_result = self._convert_detail(detail, entity_mapping)
            if detail_result.is_error():
                return ConversionResult.fail(detail_result.unwrap_error())
            item_drafts.append(detail_result.unwrap())

        return ConversionResult.ok(
            DeliveryCreatePayload(
                delivery_input=delivery_input,
                item_drafts=item_drafts,
            )
        )

    def _convert_detail(
        self,
        detail: DeliveryDetailDTO,
        entity_mapping: EntityMapping,
    ) -> ConversionResult[DeliveryItemDraft]:
        flow_index = detail.flow_index
        product_id = entity_mapping.get_product_id(flow_index)

        if not product_id:
            part_number = detail.part_number or "unknown"
            return ConversionResult.fail(
                DeliveryProductRequiredError(flow_index, part_number)
            )

        return ConversionResult.ok(
            DeliveryItemDraft(
                product_id=product_id,
                expected_quantity=detail.quantity or 0,
                received_quantity=detail.received_quantity or 0,
                damaged_quantity=detail.damaged_quantity or 0,
                discrepancy_notes=detail.description,
            )
        )

    @staticmethod
    def _generate_po_number() -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"DEL-{timestamp}"
