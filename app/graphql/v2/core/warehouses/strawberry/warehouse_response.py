import strawberry

from app.graphql.v2.core.warehouses.strawberry.warehouse_lite_response import (
    WarehouseLiteResponse,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_member_response import (
    WarehouseMemberResponse,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_settings_response import (
    WarehouseSettingsResponse,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_structure_response import (
    WarehouseStructureResponse,
)


@strawberry.type
class WarehouseResponse(WarehouseLiteResponse):
    """Full response for warehouses - extends Lite with collections.

    Note: Address information is managed separately via the Address model
    using source_id = warehouse.id and source_type = FACTORY.
    """

    @strawberry.field
    def members(self) -> list[WarehouseMemberResponse]:
        return WarehouseMemberResponse.from_orm_model_list(self._instance.members)

    @strawberry.field
    def settings(self) -> WarehouseSettingsResponse | None:
        return WarehouseSettingsResponse.from_orm_model_optional(
            self._instance.settings
        )

    @strawberry.field
    def structure(self) -> list[WarehouseStructureResponse]:
        return WarehouseStructureResponse.from_orm_model_list(self._instance.structure)
