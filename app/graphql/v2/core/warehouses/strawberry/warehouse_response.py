"""Strawberry response types for warehouses."""

from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import (
    Warehouse,
    WarehouseMember,
    WarehouseSettings,
    WarehouseStructure,
)

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.warehouses.strawberry.enums import (
    WarehouseMemberRole,
    WarehouseStructureCode,
)


@strawberry.type
class WarehouseStructureResponse(DTOMixin[WarehouseStructure]):
    """Response type for warehouse structure (location level configuration)."""

    _instance: strawberry.Private[WarehouseStructure]
    id: UUID
    warehouse_id: UUID
    code: WarehouseStructureCode
    level_order: int

    @classmethod
    def from_orm_model(cls, model: WarehouseStructure) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            warehouse_id=model.warehouse_id,
            code=WarehouseStructureCode(model.code.value),
            level_order=model.level_order,
        )


@strawberry.type
class WarehouseSettingsResponse(DTOMixin[WarehouseSettings]):
    """Response type for warehouse settings."""

    _instance: strawberry.Private[WarehouseSettings]
    id: UUID
    warehouse_id: UUID
    auto_generate_codes: bool
    require_location: bool
    show_in_pick_lists: bool
    generate_qr_codes: bool

    @classmethod
    def from_orm_model(cls, model: WarehouseSettings) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            warehouse_id=model.warehouse_id,
            auto_generate_codes=model.auto_generate_codes,
            require_location=model.require_location,
            show_in_pick_lists=model.show_in_pick_lists,
            generate_qr_codes=model.generate_qr_codes,
        )


@strawberry.type
class WarehouseMemberResponse(DTOMixin[WarehouseMember]):
    """Response type for warehouse members."""

    _instance: strawberry.Private[WarehouseMember]
    id: UUID
    warehouse_id: UUID
    user_id: UUID
    role: WarehouseMemberRole
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: WarehouseMember) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            warehouse_id=model.warehouse_id,
            user_id=model.user_id,
            role=WarehouseMemberRole(model.role.value),
            created_at=model.created_at,
        )


@strawberry.type
class WarehouseResponse(DTOMixin[Warehouse]):
    """Response type for warehouses.

    Note: Address information is managed separately via the Address model
    using source_id = warehouse.id and source_type = FACTORY.
    """

    _instance: strawberry.Private[Warehouse]
    id: UUID
    name: str
    status: str
    latitude: Decimal | None
    longitude: Decimal | None
    description: str | None
    is_active: bool | None
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: Warehouse) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            name=model.name,
            status=model.status,
            latitude=model.latitude,
            longitude=model.longitude,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    @strawberry.field
    def members(self) -> list[WarehouseMemberResponse]:
        """Get warehouse members (eager-loaded via repository)."""
        return WarehouseMemberResponse.from_orm_model_list(self._instance.members)

    @strawberry.field
    def settings(self) -> WarehouseSettingsResponse | None:
        """Get warehouse settings (eager-loaded via repository)."""
        return WarehouseSettingsResponse.from_orm_model_optional(
            self._instance.settings
        )

    @strawberry.field
    def structure(self) -> list[WarehouseStructureResponse]:
        """Get warehouse structure (eager-loaded via repository)."""
        return WarehouseStructureResponse.from_orm_model_list(self._instance.structure)
