from uuid import UUID

import strawberry
from commons.db.v6.fulfillment.enums import FulfillmentAssignmentRole


@strawberry.input
class BulkAssignmentInput:
    fulfillment_order_ids: list[UUID]
    manager_ids: list[UUID] | None = None
    worker_ids: list[UUID] | None = None


@strawberry.input
class AssignUserInput:
    user_id: UUID
    role: FulfillmentAssignmentRole


@strawberry.input
class AddAssignmentInput:
    """Input for adding an assignment to a fulfillment order."""

    fulfillment_order_id: UUID
    user_id: UUID
    role: FulfillmentAssignmentRole
