from uuid import UUID

import strawberry
from aioinject import Injected

from app.core.constants import DEFAULT_QUERY_LIMIT, DEFAULT_QUERY_OFFSET
from app.graphql.inject import inject
from app.graphql.v2.core.backorders.services.backorder_service import BackorderService
from app.graphql.v2.core.backorders.strawberry.backorder_response import (
    BackorderResponse,
)


@strawberry.type
class BackorderQueries:
    @strawberry.field
    @inject
    async def backorders(
        self,
        service: Injected[BackorderService],
        customer_id: UUID | None = None,
        product_id: UUID | None = None,
        limit: int = DEFAULT_QUERY_LIMIT,
        offset: int = DEFAULT_QUERY_OFFSET,
    ) -> list[BackorderResponse]:
        backorder_data = await service.get_backorders(
            customer_id=customer_id,
            product_id=product_id,
            limit=limit,
            offset=offset,
        )
        return BackorderResponse.from_orm_model_list(backorder_data)
