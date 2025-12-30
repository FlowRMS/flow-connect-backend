from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.adjustments.services.adjustment_service import AdjustmentService
from app.graphql.adjustments.strawberry.adjustment_input import AdjustmentInput
from app.graphql.adjustments.strawberry.adjustment_response import AdjustmentResponse
from app.graphql.inject import inject


@strawberry.type
class AdjustmentsMutations:
    @strawberry.mutation
    @inject
    async def create_adjustment(
        self,
        input: AdjustmentInput,
        service: Injected[AdjustmentService],
    ) -> AdjustmentResponse:
        adjustment = await service.create_adjustment(adjustment_input=input)
        return AdjustmentResponse.from_orm_model(adjustment)

    @strawberry.mutation
    @inject
    async def update_adjustment(
        self,
        input: AdjustmentInput,
        service: Injected[AdjustmentService],
    ) -> AdjustmentResponse:
        adjustment = await service.update_adjustment(adjustment_input=input)
        return AdjustmentResponse.from_orm_model(adjustment)

    @strawberry.mutation
    @inject
    async def delete_adjustment(
        self,
        id: UUID,
        service: Injected[AdjustmentService],
    ) -> bool:
        return await service.delete_adjustment(adjustment_id=id)
