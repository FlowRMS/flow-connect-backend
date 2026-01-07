from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.credits.services.credit_service import CreditService
from app.graphql.credits.strawberry.credit_input import CreditInput
from app.graphql.credits.strawberry.credit_response import CreditResponse
from app.graphql.inject import inject


@strawberry.type
class CreditsMutations:
    @strawberry.mutation
    @inject
    async def create_credit(
        self,
        input: CreditInput,
        service: Injected[CreditService],
    ) -> CreditResponse:
        credit = await service.create_credit(credit_input=input)
        return CreditResponse.from_orm_model(credit)

    @strawberry.mutation
    @inject
    async def update_credit(
        self,
        input: CreditInput,
        service: Injected[CreditService],
    ) -> CreditResponse:
        credit = await service.update_credit(credit_input=input)
        return CreditResponse.from_orm_model(credit)

    @strawberry.mutation
    @inject
    async def delete_credit(
        self,
        id: UUID,
        service: Injected[CreditService],
    ) -> bool:
        return await service.delete_credit(credit_id=id)
