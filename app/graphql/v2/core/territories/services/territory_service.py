from uuid import UUID

from commons.db.v6.core.territories.territory import Territory
from commons.db.v6.core.territories.territory_manager import TerritoryManager
from commons.db.v6.core.territories.territory_type_enum import TerritoryTypeEnum
from sqlalchemy.orm import joinedload

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.v2.core.territories.repositories.territory_manager_repository import (
    TerritoryManagerRepository,
)
from app.graphql.v2.core.territories.repositories.territory_repository import (
    TerritoryRepository,
)
from app.graphql.v2.core.territories.strawberry.territory_input import TerritoryInput


class TerritoryService:
    def __init__(
        self,
        repository: TerritoryRepository,
        manager_repository: TerritoryManagerRepository,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.manager_repository = manager_repository

    async def get_by_id(self, territory_id: UUID) -> Territory:
        territory = await self.repository.get_by_id(
            territory_id,
            options=[
                joinedload(Territory.parent),
                joinedload(Territory.split_rates),
                joinedload(Territory.managers),
            ],
        )
        if not territory:
            raise NotFoundError(f"Territory with id {territory_id} not found")
        return territory

    async def get_by_id_optional(self, territory_id: UUID) -> Territory | None:
        try:
            return await self.get_by_id(territory_id)
        except Exception:
            return None

    async def create(self, input: TerritoryInput) -> Territory:
        if await self.repository.code_exists(input.code):
            raise NameAlreadyExistsError(
                f"Territory code '{input.code}' already exists"
            )

        if input.parent_id:
            parent = await self.repository.get_by_id(input.parent_id)
            if not parent:
                raise NotFoundError(
                    f"Parent territory with id {input.parent_id} not found"
                )

        territory = await self.repository.create(input.to_orm_model())
        return await self.get_by_id(territory.id)

    async def update(self, territory_id: UUID, input: TerritoryInput) -> Territory:
        if await self.repository.code_exists(input.code, exclude_id=territory_id):
            raise NameAlreadyExistsError(
                f"Territory code '{input.code}' already exists"
            )

        if input.parent_id:
            if input.parent_id == territory_id:
                raise ValueError("Territory cannot be its own parent")
            parent = await self.repository.get_by_id(input.parent_id)
            if not parent:
                raise NotFoundError(
                    f"Parent territory with id {input.parent_id} not found"
                )

        territory = input.to_orm_model()
        territory.id = territory_id
        _ = await self.repository.update(territory)
        return await self.get_by_id(territory_id)

    async def delete(self, territory_id: UUID) -> bool:
        if not await self.repository.exists(territory_id):
            raise NotFoundError(f"Territory with id {territory_id} not found")
        return await self.repository.delete(territory_id)

    async def get_by_type(
        self, territory_type: TerritoryTypeEnum, active_only: bool = True
    ) -> list[Territory]:
        return await self.repository.get_by_type(territory_type, active_only)

    async def get_children(self, parent_id: UUID) -> list[Territory]:
        return await self.repository.get_children(parent_id)

    async def get_hierarchy(self, territory_id: UUID) -> list[Territory]:
        return await self.repository.get_hierarchy(territory_id)

    async def get_all_active(self) -> list[Territory]:
        return await self.repository.get_all_active()

    async def assign_manager(self, territory_id: UUID, user_id: UUID) -> Territory:
        if not await self.repository.exists(territory_id):
            raise NotFoundError(f"Territory with id {territory_id} not found")

        existing = await self.manager_repository.get_by_territory_and_user(
            territory_id, user_id
        )
        if not existing:
            manager = TerritoryManager(user_id=user_id)
            manager.territory_id = territory_id
            _ = await self.manager_repository.create(manager)

        return await self.get_by_id(territory_id)

    async def remove_manager(self, territory_id: UUID, user_id: UUID) -> bool:
        manager = await self.manager_repository.get_by_territory_and_user(
            territory_id, user_id
        )
        if not manager:
            raise NotFoundError("Manager assignment not found")
        return await self.manager_repository.delete(manager.id)
