from uuid import UUID

import strawberry
from aioinject import Injected

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
        limit: int = 100,
        offset: int = 0,
    ) -> list[BackorderResponse]:
        return await service.get_backorders(
            customer_id=customer_id,
            product_id=product_id,
            limit=limit,
            offset=offset,
        )
