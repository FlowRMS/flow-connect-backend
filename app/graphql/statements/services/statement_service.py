from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.commission.statements import CommissionStatement
from commons.db.v6.crm.links.entity_type import EntityType

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.statements.repositories.statements_repository import (
    StatementsRepository,
)
from app.graphql.statements.strawberry.statement_input import StatementInput


class StatementService:
    def __init__(
        self,
        repository: StatementsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def find_statement_by_id(self, statement_id: UUID) -> CommissionStatement:
        return await self.repository.find_statement_by_id(statement_id)

    async def find_by_statement_number(
        self, factory_id: UUID, statement_number: str
    ) -> CommissionStatement | None:
        return await self.repository.find_by_statement_number(
            factory_id, statement_number
        )

    async def create_statement(
        self, statement_input: StatementInput
    ) -> CommissionStatement:
        if await self.repository.statement_number_exists(
            statement_input.factory_id, statement_input.statement_number
        ):
            raise NameAlreadyExistsError(statement_input.statement_number)

        statement = statement_input.to_orm_model()
        return await self.repository.create_with_balance(statement)

    async def update_statement(
        self, statement_input: StatementInput
    ) -> CommissionStatement:
        if statement_input.id is None:
            raise ValueError("ID must be provided for update")

        statement = statement_input.to_orm_model()
        statement.id = statement_input.id
        return await self.repository.update_with_balance(statement)

    async def delete_statement(self, statement_id: UUID) -> bool:
        if not await self.repository.exists(statement_id):
            raise NotFoundError(str(statement_id))
        return await self.repository.delete(statement_id)

    async def search_statements(
        self,
        search_term: str,
        limit: int = 20,
    ) -> list[CommissionStatement]:
        return await self.repository.search_by_statement_number(search_term, limit)

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[CommissionStatement]:
        return await self.repository.find_by_entity(entity_type, entity_id)

    async def find_by_factory_id(
        self, factory_id: UUID, limit: int = 25
    ) -> list[CommissionStatement]:
        return await self.repository.find_by_factory_id(factory_id, limit)
