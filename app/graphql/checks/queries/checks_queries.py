from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.checks.services.check_service import CheckService
from app.graphql.checks.strawberry.check_response import (
    CheckLiteResponse,
    CheckResponse,
)
from app.graphql.inject import inject


@strawberry.type
class ChecksQueries:
    @strawberry.field
    @inject
    async def check(
        self,
        service: Injected[CheckService],
        id: UUID,
    ) -> CheckResponse:
        check = await service.find_check_by_id(id)
        return CheckResponse.from_orm_model(check)

    @strawberry.field
    @inject
    async def check_search(
        self,
        service: Injected[CheckService],
        search_term: str,
        limit: int = 20,
    ) -> list[CheckLiteResponse]:
        return CheckLiteResponse.from_orm_model_list(
            await service.search_checks(search_term, limit)
        )

    @strawberry.field
    @inject
    async def checks_by_factory(
        self,
        service: Injected[CheckService],
        factory_id: UUID,
    ) -> list[CheckLiteResponse]:
        return CheckLiteResponse.from_orm_model_list(
            await service.find_by_factory_id(factory_id)
        )
