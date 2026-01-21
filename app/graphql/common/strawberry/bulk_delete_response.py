from uuid import UUID

import strawberry

from app.graphql.common.bulk_delete_entity_type import BulkDeleteEntityType


@strawberry.type
class BulkDeleteFailure:
    entity_id: UUID
    error: str


@strawberry.type
class BulkDeleteResult:
    entity_type: BulkDeleteEntityType
    deleted_count: int
    failed_count: int
    failures: list[BulkDeleteFailure]

    @classmethod
    def success(
        cls, entity_type: BulkDeleteEntityType, deleted_count: int
    ) -> "BulkDeleteResult":
        return cls(
            entity_type=entity_type,
            deleted_count=deleted_count,
            failed_count=0,
            failures=[],
        )

    @classmethod
    def partial(
        cls,
        entity_type: BulkDeleteEntityType,
        deleted_count: int,
        failures: list[BulkDeleteFailure],
    ) -> "BulkDeleteResult":
        return cls(
            entity_type=entity_type,
            deleted_count=deleted_count,
            failed_count=len(failures),
            failures=failures,
        )
