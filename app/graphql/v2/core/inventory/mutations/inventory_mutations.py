from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.inventory.services.inventory_item_service import (
    InventoryItemService,
)
from app.graphql.v2.core.inventory.strawberry.inventory_input import (
    AddInventoryItemInput,
    UpdateInventoryItemInput,
)
from app.graphql.v2.core.inventory.strawberry.inventory_item_response import (
    InventoryItemResponse,
)


@strawberry.type
class InventoryMutations:
    @strawberry.mutation
    @inject
    async def add_inventory_item(
        self,
        service: Injected[InventoryItemService],
        input: AddInventoryItemInput,
    ) -> InventoryItemResponse:
        item = input.to_orm_model()
        created_item = await service.add_item(item)
        return InventoryItemResponse.from_orm_model(created_item)

    @strawberry.mutation
    @inject
    async def delete_inventory_item(
        self,
        service: Injected[InventoryItemService],
        id: UUID,
    ) -> bool:
        return await service.delete(id)

    @strawberry.mutation
    @inject
    async def update_inventory_item(
        self,
        service: Injected[InventoryItemService],
        input: UpdateInventoryItemInput,
    ) -> InventoryItemResponse:
        updated_item = await service.update_item(
            item_id=input.id,
            location_id=input.location_id,
            quantity=input.quantity,
            status=input.status,
        )
        return InventoryItemResponse.from_orm_model(updated_item)
