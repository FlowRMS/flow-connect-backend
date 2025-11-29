from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.addresses.models.address_model import CompanyAddress
from app.graphql.addresses.repositories.addresses_repository import AddressesRepository
from app.graphql.addresses.strawberry.address_input import AddressInput


class AddressesService:
    """Service for Addresses entity business logic."""

    def __init__(
        self,
        repository: AddressesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def create_address(self, address_input: AddressInput) -> CompanyAddress:
        return await self.repository.create(address_input.to_orm_model())

    async def delete_address(self, address_id: UUID | str) -> bool:
        if not await self.repository.exists(address_id):
            raise NotFoundError(str(address_id))
        return await self.repository.delete(address_id)

    async def get_address(self, address_id: UUID | str) -> CompanyAddress:
        address = await self.repository.get_by_id(address_id)
        if not address:
            raise NotFoundError(str(address_id))
        return address

    async def list_addresses(
        self, limit: int = 100, offset: int = 0
    ) -> list[CompanyAddress]:
        """List all addresses with pagination."""
        return await self.repository.list_all(limit=limit, offset=offset)

    async def get_addresses_by_company(self, company_id: UUID) -> list[CompanyAddress]:
        return await self.repository.get_by_company_id(company_id)
