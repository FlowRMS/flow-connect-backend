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
from app.graphql.pre_opportunities.services.pre_opportunities_service import (
    PreOpportunitiesService,
)


class PreOpportunityBulkDeleteStrategy(BulkDeleteStrategy):
    def __init__(
        self,
        pre_opportunity_service: PreOpportunitiesService,
        session: AsyncSession,
    ) -> None:
        super().__init__()
        self.pre_opportunity_service = pre_opportunity_service
        self.session = session

    @override
    def get_supported_entity_type(self) -> BulkDeleteEntityType:
        return BulkDeleteEntityType.PRE_OPS

    @override
    async def delete_entities(self, entity_ids: list[UUID]) -> BulkDeleteResult:
        deleted_count = 0
        failures: list[BulkDeleteFailure] = []

        for entity_id in entity_ids:
            async with self.session.begin_nested():
                try:
                    _ = await self.pre_opportunity_service.delete_pre_opportunity(
                        entity_id
                    )
                    deleted_count += 1
                except NotFoundError:
                    failures.append(
                        BulkDeleteFailure(
                            entity_id=entity_id,
                            error=f"Pre-opportunity with id {entity_id} not found",
                        )
                    )
                except DeletionError as e:
                    failures.append(
                        BulkDeleteFailure(entity_id=entity_id, error=str(e))
                    )

        if failures:
            return BulkDeleteResult.partial(
                entity_type=BulkDeleteEntityType.PRE_OPS,
                deleted_count=deleted_count,
                failures=failures,
            )

        return BulkDeleteResult.success(
            entity_type=BulkDeleteEntityType.PRE_OPS,
            deleted_count=deleted_count,
        )
