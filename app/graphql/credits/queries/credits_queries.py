from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.credits.services.credit_service import CreditService
from app.graphql.credits.strawberry.credit_response import (
    CreditLiteResponse,
    CreditResponse,
)
from app.graphql.inject import inject


@strawberry.type
class CreditsQueries:
    @strawberry.field
    @inject
    async def credit(
        self,
        service: Injected[CreditService],
        id: UUID,
    ) -> CreditResponse:
        credit = await service.find_credit_by_id(id)
        return CreditResponse.from_orm_model(credit)

    @strawberry.field
    @inject
    async def credit_search(
        self,
        service: Injected[CreditService],
        search_term: str,
        limit: int = 20,
    ) -> list[CreditLiteResponse]:
        return CreditLiteResponse.from_orm_model_list(
            await service.search_credits(search_term, limit)
        )
