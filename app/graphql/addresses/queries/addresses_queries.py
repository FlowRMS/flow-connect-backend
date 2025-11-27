from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.addresses.services.addresses_service import AddressesService
from app.graphql.addresses.strawberry.address_response import AddressResponse
from app.graphql.inject import inject


@strawberry.type
class AddressesQueries:
    @strawberry.field
    @inject
    async def address(
        self,
        id: UUID,
        service: Injected[AddressesService],
    ) -> AddressResponse:
        """Get an address by ID."""
        return AddressResponse.from_orm_model(await service.get_address(id))

    @strawberry.field
    @inject
    async def addresses(
        self,
        service: Injected[AddressesService],
        limit: int = 100,
        offset: int = 0,
    ) -> list[AddressResponse]:
        addresses = await service.list_addresses(limit=limit, offset=offset)
        return AddressResponse.from_orm_model_list(addresses)

    @strawberry.field
    @inject
    async def addresses_by_company(
        self,
        company_id: UUID,
        service: Injected[AddressesService],
    ) -> list[AddressResponse]:
        addresses = await service.get_addresses_by_company(company_id)
        return AddressResponse.from_orm_model_list(addresses)
