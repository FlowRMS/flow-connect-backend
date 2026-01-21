from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import PackingBox, PackingBoxItem

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class PackingBoxItemResponse(DTOMixin[PackingBoxItem]):
    _instance: strawberry.Private[PackingBoxItem]
    id: UUID
    fulfillment_line_item_id: UUID
    quantity: Decimal

    @classmethod
    def from_orm_model(cls, model: PackingBoxItem) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            fulfillment_line_item_id=model.fulfillment_line_item_id,
            quantity=model.quantity,
        )


@strawberry.type
class PackingBoxResponse(DTOMixin[PackingBox]):
    _instance: strawberry.Private[PackingBox]
    id: UUID
    box_number: int
    container_type_id: UUID | None
    length: Decimal | None
    width: Decimal | None
    height: Decimal | None
    weight: Decimal | None
    tracking_number: str | None
    label_printed_at: datetime | None
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: PackingBox) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            box_number=model.box_number,
            container_type_id=model.container_type_id,
            length=model.length,
            width=model.width,
            height=model.height,
            weight=model.weight,
            tracking_number=model.tracking_number,
            label_printed_at=model.label_printed_at,
            created_at=model.created_at,
        )

    @strawberry.field
    async def container_type_name(self) -> str | None:
        container_type = await self._instance.awaitable_attrs.container_type
        return container_type.name if container_type else None

    @strawberry.field
    async def items(self) -> list[PackingBoxItemResponse]:
        items = await self._instance.awaitable_attrs.items
        return PackingBoxItemResponse.from_orm_model_list(items)
