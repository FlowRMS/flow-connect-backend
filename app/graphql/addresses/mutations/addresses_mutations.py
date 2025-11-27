from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.addresses.services.addresses_service import AddressesService
from app.graphql.addresses.strawberry.address_input import AddressInput
from app.graphql.addresses.strawberry.address_response import AddressResponse
from app.graphql.inject import inject


@strawberry.type
class AddressesMutations:
    @strawberry.mutation
    @inject
    async def create_address(
        self,
        input: AddressInput,
        service: Injected[AddressesService],
    ) -> AddressResponse:
        return AddressResponse.from_orm_model(
            await service.create_address(address_input=input)
        )

    @strawberry.mutation
    @inject
    async def delete_address(
        self,
        id: UUID,
        service: Injected[AddressesService],
    ) -> bool:
        return await service.delete_address(address_id=id)
