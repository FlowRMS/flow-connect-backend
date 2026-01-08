from uuid import UUID

from commons.db.v6.commission.orders.order_detail import OrderDetail
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.v2.core.backorders.repositories.backorder_repository import (
    BackorderRepository,
)



from app.core.constants import DEFAULT_QUERY_LIMIT, DEFAULT_QUERY_OFFSET

class BackorderService:
    def __init__(
        self,
        repository: BackorderRepository,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.context_wrapper = context_wrapper
        self.session = session

    async def get_backorders(
        self,
        customer_id: UUID | None = None,
        product_id: UUID | None = None,
        limit: int = DEFAULT_QUERY_LIMIT,
        offset: int = DEFAULT_QUERY_OFFSET,
    ) -> list[OrderDetail]:
        return await self.repository.get_backorders(
            customer_id=customer_id,
            product_id=product_id,
            limit=limit,
            offset=offset,
        )

