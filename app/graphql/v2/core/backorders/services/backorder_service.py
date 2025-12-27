from uuid import UUID

from app.graphql.v2.core.backorders.repositories.backorder_repository import (
    BackorderRepository,
)
from app.graphql.v2.core.backorders.strawberry.backorder_response import (
    BackorderResponse,
)


class BackorderService:
    def __init__(
        self,
        repository: BackorderRepository,
    ) -> None:
        self.repository = repository

    async def get_backorders(
        self,
        customer_id: UUID | None = None,
        product_id: UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BackorderResponse]:
        return await self.repository.get_backorders(
            customer_id=customer_id,
            product_id=product_id,
            limit=limit,
            offset=offset,
        )
