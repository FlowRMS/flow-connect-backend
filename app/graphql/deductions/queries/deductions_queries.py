from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.deductions.services.deduction_service import DeductionService
from app.graphql.deductions.strawberry.deduction_response import (
    DeductionLiteResponse,
    DeductionResponse,
)
from app.graphql.inject import inject


@strawberry.type
class DeductionsQueries:
    @strawberry.field
    @inject
    async def deduction(
        self,
        service: Injected[DeductionService],
        id: UUID,
    ) -> DeductionResponse:
        deduction = await service.find_deduction_by_id(id)
        return DeductionResponse.from_orm_model(deduction)

    @strawberry.field
    @inject
    async def deductions_by_check(
        self,
        service: Injected[DeductionService],
        check_id: UUID,
    ) -> list[DeductionResponse]:
        deductions = await service.find_by_check_id(check_id)
        return DeductionResponse.from_orm_model_list(deductions)

    @strawberry.field
    @inject
    async def deduction_search(
        self,
        service: Injected[DeductionService],
        search_term: str,
        limit: int = 20,
    ) -> list[DeductionLiteResponse]:
        return DeductionLiteResponse.from_orm_model_list(
            await service.search_deductions(search_term, limit)
        )
