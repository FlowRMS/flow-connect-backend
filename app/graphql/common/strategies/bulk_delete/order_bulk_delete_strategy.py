from typing import override
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.common_errors import DeletionError, NotFoundError
from app.graphql.common.bulk_delete_entity_type import BulkDeleteEntityType
from app.graphql.common.interfaces.bulk_delete_strategy import BulkDeleteStrategy
from app.graphql.common.strawberry.bulk_delete_response import (
    BulkDeleteFailure,
    BulkDeleteResult,
)
from app.graphql.invoices.services.invoice_service import InvoiceService
from app.graphql.orders.services.order_service import OrderService


class OrderBulkDeleteStrategy(BulkDeleteStrategy):
    def __init__(
        self,
        order_service: OrderService,
        invoice_service: InvoiceService,
        session: AsyncSession,
    ) -> None:
        super().__init__()
        self.order_service = order_service
        self.invoice_service = invoice_service
        self.session = session

    @override
    def get_supported_entity_type(self) -> BulkDeleteEntityType:
        return BulkDeleteEntityType.ORDERS

    async def _has_invoices(self, order_id: UUID) -> bool:
        invoices = await self.invoice_service.find_invoices_by_order_id(order_id)
        return len(invoices) > 0

    @override
    async def delete_entities(self, entity_ids: list[UUID]) -> BulkDeleteResult:
        deleted_count = 0
        failures: list[BulkDeleteFailure] = []

        for entity_id in entity_ids:
            if await self._has_invoices(entity_id):
                failures.append(
                    BulkDeleteFailure(
                        entity_id=entity_id,
                        error="Order has invoices and cannot be deleted",
                    )
                )
                continue

            async with self.session.begin_nested():
                try:
                    _ = await self.order_service.delete_order(entity_id)
                    deleted_count += 1
                except NotFoundError:
                    failures.append(
                        BulkDeleteFailure(
                            entity_id=entity_id,
                            error=f"Order with id {entity_id} not found",
                        )
                    )
                except DeletionError as e:
                    failures.append(
                        BulkDeleteFailure(entity_id=entity_id, error=str(e))
                    )

        if failures:
            return BulkDeleteResult.partial(
                entity_type=BulkDeleteEntityType.ORDERS,
                deleted_count=deleted_count,
                failures=failures,
            )

        return BulkDeleteResult.success(
            entity_type=BulkDeleteEntityType.ORDERS,
            deleted_count=deleted_count,
        )
