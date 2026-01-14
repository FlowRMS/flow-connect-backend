from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.commission import Check
from commons.db.v6.commission.checks.enums import CheckStatus
from commons.db.v6.crm.links.entity_type import EntityType

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.checks.repositories.checks_repository import ChecksRepository
from app.graphql.checks.strawberry.check_input import CheckInput


class CheckService:
    def __init__(
        self,
        repository: ChecksRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def find_check_by_id(self, check_id: UUID) -> Check:
        return await self.repository.find_check_by_id(check_id)

    async def create_check(self, check_input: CheckInput) -> Check:
        if await self.repository.check_number_exists(
            check_input.factory_id, check_input.check_number
        ):
            raise NameAlreadyExistsError(check_input.check_number)

        check = check_input.to_orm_model()
        created = await self.repository.create(check)
        return await self.repository.find_check_by_id(created.id)

    async def update_check(self, check_input: CheckInput) -> Check:
        if check_input.id is None:
            raise ValueError("ID must be provided for update")

        check = check_input.to_orm_model()
        check.id = check_input.id
        updated = await self.repository.update(check)
        return await self.repository.find_check_by_id(updated.id)

    async def delete_check(self, check_id: UUID) -> bool:
        if not await self.repository.exists(check_id):
            raise NotFoundError(str(check_id))
        return await self.repository.delete(check_id)

    async def search_checks(self, search_term: str, limit: int = 20) -> list[Check]:
        return await self.repository.search_by_check_number(search_term, limit)

    async def find_checks_by_job_id(self, job_id: UUID) -> list[Check]:
        return await self.repository.find_by_job_id(job_id)

    async def find_by_factory_id(self, factory_id: UUID) -> list[Check]:
        return await self.repository.find_by_factory_id(factory_id)

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Check]:
        return await self.repository.find_by_entity(entity_type, entity_id)

    async def unpost_check(self, check_id: UUID) -> Check:
        check = await self.repository.find_check_by_id(check_id)
        if check.status != CheckStatus.POSTED:
            raise ValueError("Check must be in POSTED status to unpost")

        check.status = CheckStatus.OPEN
        _ = await self.repository.update(check)
        return await self.repository.find_check_by_id(check_id)
