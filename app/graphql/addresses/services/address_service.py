from uuid import UUID

from commons.db.v6.core.addresses.address import Address, AddressSourceTypeEnum

from app.errors.common_errors import NotFoundError
from app.graphql.addresses.repositories.address_repository import AddressRepository
from app.graphql.addresses.strawberry.address_input import AddressInput


class AddressService:
    def __init__(self, repository: AddressRepository) -> None:
        super().__init__()
        self.repository = repository

    async def get_by_id(self, address_id: UUID) -> Address:
        address = await self.repository.get_by_id(address_id)
        if not address:
            raise NotFoundError(f"Address with id {address_id} not found")
        return address

    async def list_by_source(
        self,
        source_type: AddressSourceTypeEnum,
        source_id: UUID,
    ) -> list[Address]:
        return await self.repository.list_by_source(source_type, source_id)

    async def list_by_source_id(self, source_id: UUID) -> list[Address]:
        return await self.repository.list_by_source_id(source_id)

    async def create(self, address_input: AddressInput) -> Address:
        address = await self.repository.create(address_input.to_orm_model())
        return await self.get_by_id(address.id)

    async def update(self, address_id: UUID, address_input: AddressInput) -> Address:
        address = address_input.to_orm_model()
        address.id = address_id
        _ = await self.repository.update(address)
        return await self.get_by_id(address_id)

    async def delete(self, address_id: UUID) -> bool:
        if not await self.repository.exists(address_id):
            raise NotFoundError(f"Address with id {address_id} not found")
        return await self.repository.delete(address_id)
