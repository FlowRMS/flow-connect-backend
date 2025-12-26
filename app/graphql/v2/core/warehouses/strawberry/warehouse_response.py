"""Strawberry response types for warehouses."""

from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry

from commons.db.v6 import (
    Warehouse,
    WarehouseMember,
    WarehouseMemberRole,
    WarehouseSettings,
    WarehouseStructure,
)

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.warehouses.strawberry.warehouse_input import (
    WarehouseMemberRoleGQL,
)


@strawberry.type
class WarehouseStructureResponse(DTOMixin[WarehouseStructure]):
    """Response type for warehouse structure (location level configuration)."""

    _instance: strawberry.Private[WarehouseStructure]
    id: UUID
    warehouse_id: UUID
    code: str  # 'section', 'aisle', etc.
    level_order: int

    @classmethod
    def from_orm_model(cls, model: WarehouseStructure) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            warehouse_id=model.warehouse_id,
            code=model.code,
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
    role: WarehouseMemberRoleGQL
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: WarehouseMember) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            warehouse_id=model.warehouse_id,
            user_id=model.user_id,
            role=WarehouseMemberRoleGQL(model.role.value),
            created_at=model.created_at,
        )


@strawberry.type
class WarehouseResponse(DTOMixin[Warehouse]):
    """Response type for warehouses."""

    _instance: strawberry.Private[Warehouse]
    id: UUID
    name: str
    status: str
    address_line_1: str | None  # Mapped from address_line
    address_line_2: str | None
    city: str | None
    state: str | None
    postal_code: str | None  # Mapped from zip
    country: str | None
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
            address_line_1=model.address_line,
            address_line_2=model.address_line_2,
            city=model.city,
            state=model.state,
            postal_code=model.zip,
            country=model.country,
            latitude=model.latitude,
            longitude=model.longitude,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
        )

    @strawberry.field
    async def members(self) -> list[WarehouseMemberResponse]:
        """Get warehouse members."""
        members = await self._instance.awaitable_attrs.members
        return WarehouseMemberResponse.from_orm_model_list(members)

    @strawberry.field
    async def settings(self) -> WarehouseSettingsResponse | None:
        """Get warehouse settings."""
        settings = await self._instance.awaitable_attrs.settings
        return WarehouseSettingsResponse.from_orm_model_optional(settings)

    @strawberry.field
    async def structure(self) -> list[WarehouseStructureResponse]:
        """Get warehouse structure (location level configuration)."""
        structure = await self._instance.awaitable_attrs.structure
        return WarehouseStructureResponse.from_orm_model_list(structure)
