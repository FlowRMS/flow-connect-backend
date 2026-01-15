from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.checks.services.check_service import CheckService
from app.graphql.checks.strawberry.check_input import CheckInput
from app.graphql.checks.strawberry.check_response import CheckResponse
from app.graphql.inject import inject


@strawberry.type
class ChecksMutations:
    @strawberry.mutation
    @inject
    async def create_check(
        self,
        input: CheckInput,
        service: Injected[CheckService],
    ) -> CheckResponse:
        check = await service.create_check(check_input=input)
        return CheckResponse.from_orm_model(check)

    @strawberry.mutation
    @inject
    async def update_check(
        self,
        input: CheckInput,
        service: Injected[CheckService],
    ) -> CheckResponse:
        check = await service.update_check(check_input=input)
        return CheckResponse.from_orm_model(check)

    @strawberry.mutation
    @inject
    async def delete_check(
        self,
        id: UUID,
        service: Injected[CheckService],
    ) -> bool:
        return await service.delete_check(check_id=id)

    @strawberry.mutation
    @inject
    async def unpost_check(
        self,
        check_id: UUID,
        service: Injected[CheckService],
    ) -> CheckResponse:
        check = await service.unpost_check(check_id=check_id)
        return CheckResponse.from_orm_model(check)

    @strawberry.mutation
    @inject
    async def post_check(
        self,
        check_id: UUID,
        service: Injected[CheckService],
    ) -> CheckResponse:
        check = await service.post_check(check_id=check_id)
        return CheckResponse.from_orm_model(check)
