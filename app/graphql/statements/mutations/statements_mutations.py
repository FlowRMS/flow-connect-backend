from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.statements.services.statement_service import StatementService
from app.graphql.statements.strawberry.statement_input import StatementInput
from app.graphql.statements.strawberry.statement_response import StatementResponse


@strawberry.type
class StatementsMutations:
    @strawberry.mutation
    @inject
    async def create_statement(
        self,
        input: StatementInput,
        service: Injected[StatementService],
    ) -> StatementResponse:
        statement = await service.create_statement(statement_input=input)
        return StatementResponse.from_orm_model(statement)

    @strawberry.mutation
    @inject
    async def update_statement(
        self,
        input: StatementInput,
        service: Injected[StatementService],
    ) -> StatementResponse:
        statement = await service.update_statement(statement_input=input)
        return StatementResponse.from_orm_model(statement)

    @strawberry.mutation
    @inject
    async def delete_statement(
        self,
        id: UUID,
        service: Injected[StatementService],
    ) -> bool:
        return await service.delete_statement(statement_id=id)
