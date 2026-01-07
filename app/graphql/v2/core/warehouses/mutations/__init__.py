"""Warehouse mutations."""

from app.graphql.v2.core.warehouses.mutations.warehouse_location_mutations import (
    WarehouseLocationMutations,
)
from app.graphql.v2.core.warehouses.mutations.warehouses_mutations import (
    WarehousesMutations,
)

__all__ = ["WarehouseLocationMutations", "WarehousesMutations"]
