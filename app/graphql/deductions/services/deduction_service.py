from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.commission import Deduction

from app.errors.common_errors import NotFoundError
from app.graphql.deductions.repositories.deductions_repository import (
    DeductionsRepository,
)
from app.graphql.deductions.strawberry.deduction_input import DeductionInput


class DeductionService:
    def __init__(
        self,
        repository: DeductionsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def find_deduction_by_id(self, deduction_id: UUID) -> Deduction:
        return await self.repository.find_deduction_by_id(deduction_id)

    async def create_deduction(self, deduction_input: DeductionInput) -> Deduction:
        deduction = deduction_input.to_orm_model()
        created = await self.repository.create(deduction)
        return await self.repository.find_deduction_by_id(created.id)

    async def update_deduction(self, deduction_input: DeductionInput) -> Deduction:
        if deduction_input.id is None:
            raise ValueError("ID must be provided for update")

        deduction = deduction_input.to_orm_model()
        deduction.id = deduction_input.id
        updated = await self.repository.update(deduction)
        return await self.repository.find_deduction_by_id(updated.id)

    async def delete_deduction(self, deduction_id: UUID) -> bool:
        if not await self.repository.exists(deduction_id):
            raise NotFoundError(str(deduction_id))
        return await self.repository.delete(deduction_id)

    async def find_by_check_id(self, check_id: UUID) -> list[Deduction]:
        return await self.repository.find_by_check_id(check_id)

    async def search_deductions(
        self, search_term: str, limit: int = 20
    ) -> list[Deduction]:
        return await self.repository.search_by_reason(search_term, limit)
