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
from app.graphql.credits.services.credit_service import CreditService


class CreditBulkDeleteStrategy(BulkDeleteStrategy):
    def __init__(self, credit_service: CreditService, session: AsyncSession) -> None:
        super().__init__()
        self.credit_service = credit_service
        self.session = session

    @override
    def get_supported_entity_type(self) -> BulkDeleteEntityType:
        return BulkDeleteEntityType.CREDITS

    @override
    async def delete_entities(self, entity_ids: list[UUID]) -> BulkDeleteResult:
        deleted_count = 0
        failures: list[BulkDeleteFailure] = []

        for entity_id in entity_ids:
            async with self.session.begin_nested():
                try:
                    _ = await self.credit_service.delete_credit(entity_id)
                    deleted_count += 1
                except NotFoundError:
                    failures.append(
                        BulkDeleteFailure(
                            entity_id=entity_id,
                            error=f"Credit with id {entity_id} not found",
                        )
                    )
                except DeletionError as e:
                    failures.append(
                        BulkDeleteFailure(entity_id=entity_id, error=str(e))
                    )

        if failures:
            return BulkDeleteResult.partial(
                entity_type=BulkDeleteEntityType.CREDITS,
                deleted_count=deleted_count,
                failures=failures,
            )

        return BulkDeleteResult.success(
            entity_type=BulkDeleteEntityType.CREDITS,
            deleted_count=deleted_count,
        )
