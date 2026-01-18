from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.statements.services.statement_service import StatementService
from app.graphql.statements.strawberry.statement_response import (
    StatementLiteResponse,
    StatementResponse,
)


@strawberry.type
class StatementsQueries:
    @strawberry.field
    @inject
    async def statement(
        self,
        service: Injected[StatementService],
        id: UUID,
    ) -> StatementResponse:
        statement = await service.find_statement_by_id(id)
        return StatementResponse.from_orm_model(statement)

    @strawberry.field
    @inject
    async def statement_search(
        self,
        service: Injected[StatementService],
        search_term: str,
        limit: int = 20,
    ) -> list[StatementLiteResponse]:
        return StatementLiteResponse.from_orm_model_list(
            await service.search_statements(search_term, limit)
        )

    @strawberry.field
    @inject
    async def statements_by_factory_id(
        self,
        service: Injected[StatementService],
        factory_id: UUID,
        limit: int = 25,
    ) -> list[StatementLiteResponse]:
        return StatementLiteResponse.from_orm_model_list(
            await service.find_by_factory_id(factory_id, limit)
        )
