from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.commission import Credit

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.credits.repositories.credits_repository import CreditsRepository
from app.graphql.credits.strawberry.credit_input import CreditInput


class CreditService:
    def __init__(
        self,
        repository: CreditsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def find_credit_by_id(self, credit_id: UUID) -> Credit:
        return await self.repository.find_credit_by_id(credit_id)

    async def create_credit(self, credit_input: CreditInput) -> Credit:
        if await self.repository.credit_number_exists(
            credit_input.order_id, credit_input.credit_number
        ):
            raise NameAlreadyExistsError(credit_input.credit_number)

        credit = credit_input.to_orm_model()
        return await self.repository.create_with_balance(credit)

    async def update_credit(self, credit_input: CreditInput) -> Credit:
        if credit_input.id is None:
            raise ValueError("ID must be provided for update")

        credit = credit_input.to_orm_model()
        credit.id = credit_input.id
        return await self.repository.update_with_balance(credit)

    async def delete_credit(self, credit_id: UUID) -> bool:
        if not await self.repository.exists(credit_id):
            raise NotFoundError(str(credit_id))
        return await self.repository.delete(credit_id)

    async def search_credits(self, search_term: str, limit: int = 20) -> list[Credit]:
        return await self.repository.search_by_credit_number(search_term, limit)

    async def find_credits_by_job_id(self, job_id: UUID) -> list[Credit]:
        return await self.repository.find_by_job_id(job_id)
