from uuid import UUID

import strawberry


@strawberry.input
class BulkAssignmentInput:
    fulfillment_order_ids: list[UUID]
    manager_ids: list[UUID] | None = None
    worker_ids: list[UUID] | None = None
