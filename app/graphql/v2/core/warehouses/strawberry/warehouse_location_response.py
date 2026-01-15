from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import (
    LocationProductAssignment,
    WarehouseLocation,
    WarehouseStructureCode,
)

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class LocationProductAssignmentResponse(DTOMixin[LocationProductAssignment]):
    _instance: strawberry.Private[LocationProductAssignment]
    id: UUID
    location_id: UUID
    product_id: UUID
    quantity: Decimal
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: LocationProductAssignment) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            location_id=model.location_id,
            product_id=model.product_id,
            quantity=model.quantity,
            created_at=model.created_at,
        )


@strawberry.type
class WarehouseLocationResponse(DTOMixin[WarehouseLocation]):
    _instance: strawberry.Private[WarehouseLocation]
    id: UUID
    warehouse_id: UUID
    parent_id: UUID | None
    level: WarehouseStructureCode
    name: str
    code: str | None
    description: str | None
    is_active: bool
    sort_order: int
    x: Decimal | None
    y: Decimal | None
    width: Decimal | None
    height: Decimal | None
    rotation: Decimal | None
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: WarehouseLocation) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            warehouse_id=model.warehouse_id,
            parent_id=model.parent_id,
            level=WarehouseStructureCode(model.level.value),
            name=model.name,
            code=model.code,
            description=model.description,
            is_active=model.is_active,
            sort_order=model.sort_order,
            x=model.x,
            y=model.y,
            width=model.width,
            height=model.height,
            rotation=model.rotation,
            created_at=model.created_at,
        )

    @strawberry.field
    def children(self) -> list["WarehouseLocationResponse"]:
        # Access children directly since they are eagerly loaded via joinedload
        # Using awaitable_attrs causes lazy loading errors when session is closed
        return WarehouseLocationResponse.from_orm_model_list(self._instance.children)

    @strawberry.field
    def product_assignments(self) -> list[LocationProductAssignmentResponse]:
        # Access product_assignments directly since they are eagerly loaded via joinedload
        # Using awaitable_attrs causes lazy loading errors when session is closed
        return LocationProductAssignmentResponse.from_orm_model_list(
            self._instance.product_assignments
        )
