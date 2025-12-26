from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.addresses.services.address_service import AddressService
from app.graphql.addresses.strawberry.address_input import AddressInput
from app.graphql.addresses.strawberry.address_response import AddressResponse
from app.graphql.inject import inject


@strawberry.type
class AddressMutations:
    @strawberry.mutation
    @inject
    async def create_address(
        self,
        input: AddressInput,
        service: Injected[AddressService],
    ) -> AddressResponse:
        address = await service.create(input)
        return AddressResponse.from_orm_model(address)

    @strawberry.mutation
    @inject
    async def update_address(
        self,
        id: UUID,
        input: AddressInput,
        service: Injected[AddressService],
    ) -> AddressResponse:
        address = await service.update(id, input)
        return AddressResponse.from_orm_model(address)

    @strawberry.mutation
    @inject
    async def delete_address(
        self,
        id: UUID,
        service: Injected[AddressService],
    ) -> bool:
        return await service.delete(id)
