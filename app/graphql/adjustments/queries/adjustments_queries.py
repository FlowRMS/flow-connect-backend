from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.adjustments.services.adjustment_service import AdjustmentService
from app.graphql.adjustments.strawberry.adjustment_response import (
    AdjustmentLiteResponse,
    AdjustmentResponse,
)
from app.graphql.inject import inject


@strawberry.type
class AdjustmentsQueries:
    @strawberry.field
    @inject
    async def adjustment(
        self,
        service: Injected[AdjustmentService],
        id: UUID,
    ) -> AdjustmentResponse:
        adjustment = await service.find_adjustment_by_id(id)
        return AdjustmentResponse.from_orm_model(adjustment)

    @strawberry.field
    @inject
    async def adjustment_search(
        self,
        service: Injected[AdjustmentService],
        search_term: str,
        limit: int = 20,
    ) -> list[AdjustmentLiteResponse]:
        return AdjustmentLiteResponse.from_orm_model_list(
            await service.search_adjustments(search_term, limit)
        )
