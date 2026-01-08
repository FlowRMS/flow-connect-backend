from typing import override
from uuid import UUID

from commons.db.v6.commission import CheckDetail
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.common_errors import DeletionError, NotFoundError
from app.graphql.common.bulk_delete_entity_type import BulkDeleteEntityType
from app.graphql.common.interfaces.bulk_delete_strategy import BulkDeleteStrategy
from app.graphql.common.strawberry.bulk_delete_response import (
    BulkDeleteFailure,
    BulkDeleteResult,
)
from app.graphql.invoices.services.invoice_service import InvoiceService


class InvoiceBulkDeleteStrategy(BulkDeleteStrategy):
    def __init__(
        self,
        invoice_service: InvoiceService,
        session: AsyncSession,
    ) -> None:
        super().__init__()
        self.invoice_service = invoice_service
        self.session = session

    @override
    def get_supported_entity_type(self) -> BulkDeleteEntityType:
        return BulkDeleteEntityType.INVOICES

    async def _has_checks(self, invoice_id: UUID) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(CheckDetail)
            .where(CheckDetail.invoice_id == invoice_id)
        )
        return result.scalar_one() > 0

    @override
    async def delete_entities(self, entity_ids: list[UUID]) -> BulkDeleteResult:
        deleted_count = 0
        failures: list[BulkDeleteFailure] = []

        for entity_id in entity_ids:
            if await self._has_checks(entity_id):
                failures.append(
                    BulkDeleteFailure(
                        entity_id=entity_id,
                        error="Invoice is tied to a check and cannot be deleted",
                    )
                )
                continue

            async with self.session.begin_nested():
                try:
                    _ = await self.invoice_service.delete_invoice(entity_id)
                    deleted_count += 1
                except NotFoundError:
                    failures.append(
                        BulkDeleteFailure(
                            entity_id=entity_id,
                            error=f"Invoice with id {entity_id} not found",
                        )
                    )
                except DeletionError as e:
                    failures.append(
                        BulkDeleteFailure(entity_id=entity_id, error=str(e))
                    )

        if failures:
            return BulkDeleteResult.partial(
                entity_type=BulkDeleteEntityType.INVOICES,
                deleted_count=deleted_count,
                failures=failures,
            )

        return BulkDeleteResult.success(
            entity_type=BulkDeleteEntityType.INVOICES,
            deleted_count=deleted_count,
        )
