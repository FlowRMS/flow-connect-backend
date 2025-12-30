from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.deductions.services.deduction_service import DeductionService
from app.graphql.deductions.strawberry.deduction_input import DeductionInput
from app.graphql.deductions.strawberry.deduction_response import DeductionResponse
from app.graphql.inject import inject


@strawberry.type
class DeductionsMutations:
    @strawberry.mutation
    @inject
    async def create_deduction(
        self,
        input: DeductionInput,
        service: Injected[DeductionService],
    ) -> DeductionResponse:
        deduction = await service.create_deduction(deduction_input=input)
        return DeductionResponse.from_orm_model(deduction)

    @strawberry.mutation
    @inject
    async def update_deduction(
        self,
        input: DeductionInput,
        service: Injected[DeductionService],
    ) -> DeductionResponse:
        deduction = await service.update_deduction(deduction_input=input)
        return DeductionResponse.from_orm_model(deduction)

    @strawberry.mutation
    @inject
    async def delete_deduction(
        self,
        id: UUID,
        service: Injected[DeductionService],
    ) -> bool:
        return await service.delete_deduction(deduction_id=id)
