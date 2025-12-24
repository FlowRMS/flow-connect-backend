"""Strawberry input types for warehouses."""

from uuid import UUID

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.v2.core.warehouses.models import (
    Warehouse,
    WarehouseMember,
    WarehouseSettings,
    WarehouseStructure,
)


@strawberry.input
class WarehouseInput(BaseInputGQL[Warehouse]):
    """Input type for creating/updating warehouses."""

    name: str
    status: str = "active"
    address_line_1: str | None = None  # Maps to address_line
    address_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None  # Maps to zip
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None
    is_active: bool = True

    def to_orm_model(self) -> Warehouse:
        return Warehouse(
            name=self.name,
            status=self.status,
            address_line=self.address_line_1,
            address_line_2=self.address_line_2,
            city=self.city,
            state=self.state,
            zip=self.postal_code,
            country=self.country,
            latitude=self.latitude,  # type: ignore[arg-type]
            longitude=self.longitude,  # type: ignore[arg-type]
            description=self.description,
            is_active=self.is_active,
        )


@strawberry.input
class WarehouseMemberInput(BaseInputGQL[WarehouseMember]):
    """Input type for assigning workers to warehouses."""

    warehouse_id: UUID
    user_id: UUID
    role: int  # 1=worker, 2=manager
    role_name: str | None = None

    def to_orm_model(self) -> WarehouseMember:
        return WarehouseMember(
            warehouse_id=self.warehouse_id,
            user_id=self.user_id,
            role=self.role,
            role_name=self.role_name,
        )


@strawberry.input
class WarehouseSettingsInput(BaseInputGQL[WarehouseSettings]):
    """Input type for warehouse settings."""

    warehouse_id: UUID
    auto_generate_codes: bool = False
    require_location: bool = True
    show_in_pick_lists: bool = True
    generate_qr_codes: bool = False

    def to_orm_model(self) -> WarehouseSettings:
        return WarehouseSettings(
            warehouse_id=self.warehouse_id,
            auto_generate_codes=self.auto_generate_codes,
            require_location=self.require_location,
            show_in_pick_lists=self.show_in_pick_lists,
            generate_qr_codes=self.generate_qr_codes,
        )


@strawberry.input
class WarehouseStructureLevelInput:
    """Input type for a single location level configuration."""

    code: str  # 'section', 'aisle', 'shelf', 'bay', 'row', 'bin'
    level_order: int


@strawberry.input
class WarehouseStructureInput(BaseInputGQL[WarehouseStructure]):
    """Input type for warehouse structure (location level configuration)."""

    warehouse_id: UUID
    code: str
    level_order: int

    def to_orm_model(self) -> WarehouseStructure:
        return WarehouseStructure(
            warehouse_id=self.warehouse_id,
            code=self.code,
            level_order=self.level_order,
        )
