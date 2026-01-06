"""Strawberry input types for warehouse locations."""

from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6 import WarehouseStructureCode


@strawberry.input
class WarehouseLocationInput:
    """Input type for creating/updating warehouse locations."""

    warehouse_id: UUID
    level: WarehouseStructureCode
    name: str
    parent_id: UUID | None = None
    code: str | None = None
    description: str | None = None
    is_active: bool | None = True
    sort_order: int | None = 0

    # Visual properties for layout builder
    x: Decimal | None = None
    y: Decimal | None = None
    width: Decimal | None = None
    height: Decimal | None = None
    rotation: Decimal | None = None


@strawberry.input
class BulkWarehouseLocationInput:
    """Input type for bulk saving warehouse locations.

    Similar to WarehouseLocationInput but includes optional id for updates.
    Supports temp_id and temp_parent_id for newly created hierarchical locations.
    """

    level: WarehouseStructureCode
    name: str
    id: UUID | None = None  # For existing locations being updated
    parent_id: UUID | None = None  # Real UUID parent (for existing parents)
    temp_id: str | None = None  # Temp ID for new locations (e.g., "SECTION-123")
    temp_parent_id: str | None = None  # Temp parent ID (when parent is also new)
    code: str | None = None
    description: str | None = None
    is_active: bool | None = True
    sort_order: int | None = 0

    # Visual properties for layout builder
    x: Decimal | None = None
    y: Decimal | None = None
    width: Decimal | None = None
    height: Decimal | None = None
    rotation: Decimal | None = None


@strawberry.input
class LocationProductAssignmentInput:
    """Input type for assigning products to locations."""

    location_id: UUID
    product_id: UUID
    quantity: Decimal = Decimal(0)
