"""Strawberry input types for warehouses."""

from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6 import (
    Warehouse,
    WarehouseMember,
    WarehouseSettings,
    WarehouseStructure,
)

from app.core.strawberry.inputs import BaseInputGQL
from commons.db.v6.warehouse.warehouse_member_role import WarehouseMemberRole
from commons.db.v6.warehouse.warehouse_structure_code import WarehouseStructureCode


@strawberry.input
class WarehouseInput(BaseInputGQL[Warehouse]):
    """Input type for creating/updating warehouses.

    Note: Address information is managed separately via the Address model
    using source_id = warehouse.id and source_type = FACTORY.
    """

    name: str
    status: str = "active"
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    description: str | None = None
    is_active: bool = True

    def to_orm_model(self) -> Warehouse:
        return Warehouse(
            name=self.name,
            status=self.status,
            latitude=self.latitude,
            longitude=self.longitude,
            description=self.description,
            is_active=self.is_active,
        )


@strawberry.input
class WarehouseMemberInput(BaseInputGQL[WarehouseMember]):
    """Input type for assigning workers to warehouses."""

    warehouse_id: UUID
    user_id: UUID
    role: WarehouseMemberRole

    def to_orm_model(self) -> WarehouseMember:
        return WarehouseMember(
            warehouse_id=self.warehouse_id,
            user_id=self.user_id,
            role=self.role,
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

    code: WarehouseStructureCode
    level_order: int


@strawberry.input
class WarehouseStructureInput(BaseInputGQL[WarehouseStructure]):
    """Input type for warehouse structure (location level configuration)."""

    warehouse_id: UUID
    code: WarehouseStructureCode
    level_order: int

    def to_orm_model(self) -> WarehouseStructure:
        return WarehouseStructure(
            warehouse_id=self.warehouse_id,
            code=self.code,
            level_order=self.level_order,
        )
