from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.core.addresses.address import AddressSourceTypeEnum

from app.graphql.addresses.services.address_service import AddressService
from app.graphql.addresses.strawberry.address_response import AddressResponse
from app.graphql.inject import inject


@strawberry.type
class AddressQueries:
    @strawberry.field
    @inject
    async def address(
        self,
        id: UUID,
        service: Injected[AddressService],
    ) -> AddressResponse:
        address = await service.get_by_id(id)
        return AddressResponse.from_orm_model(address)

    @strawberry.field
    @inject
    async def addresses_by_source(
        self,
        source_type: AddressSourceTypeEnum,
        source_id: UUID,
        service: Injected[AddressService],
    ) -> list[AddressResponse]:
        addresses = await service.list_by_source(source_type, source_id)
        return AddressResponse.from_orm_model_list(addresses)

    @strawberry.field
    @inject
    async def addresses_by_source_id(
        self,
        source_id: UUID,
        service: Injected[AddressService],
    ) -> list[AddressResponse]:
        addresses = await service.list_by_source_id(source_id)
        return AddressResponse.from_orm_model_list(addresses)
