from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.inventory.services.inventory_file_service import (
    InventoryFileService,
)
from app.graphql.v2.core.inventory.services.inventory_item_service import (
    InventoryItemService,
)
from app.graphql.v2.core.inventory.services.inventory_service import (
    InventoryService,
)
from app.graphql.v2.core.inventory.strawberry.inventory_import_summary import (
    InventoryImportSummary,
)
from app.graphql.v2.core.inventory.strawberry.inventory_input import (
    AddInventoryItemInput,
    CreateInventoryInput,
    UpdateInventoryItemInput,
)
from app.graphql.v2.core.inventory.strawberry.inventory_item_response import (
    InventoryItemResponse,
)
from app.graphql.v2.core.inventory.strawberry.inventory_response import (
    InventoryResponse,
)


@strawberry.type
class InventoryMutations:
    @strawberry.mutation
    @inject
    async def create_inventory(
        self,
        service: Injected[InventoryService],
        input: CreateInventoryInput,
    ) -> InventoryResponse:
        inventory = input.to_orm_model()
        created_inventory = await service.create(inventory)
        return InventoryResponse.from_orm_model(created_inventory)

    @strawberry.mutation
    @inject
    async def delete_inventory(
        self,
        service: Injected[InventoryService],
        id: UUID,
    ) -> bool:
        return await service.delete(id)

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

    @strawberry.mutation
    @inject
    async def export_inventory(
        self,
        warehouse_id: UUID,
        service: Injected[InventoryFileService],
    ) -> str:
        return await service.export_inventory_csv(warehouse_id)

    @strawberry.mutation
    @inject
    async def import_inventory(
        self,
        warehouse_id: UUID,
        file: str,
        service: Injected[InventoryFileService],
    ) -> InventoryImportSummary:
        stats = await service.import_inventory_csv(warehouse_id, file)
        return InventoryImportSummary(
            processed=stats["processed"],
            created=stats["created"],
            updated=stats["updated"],
            errors=stats["errors"],
            skipped=stats["skipped"],
        )
