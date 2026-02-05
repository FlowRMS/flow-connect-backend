from uuid import UUID

import strawberry
from commons.db.v6.fulfillment.enums import FulfillmentAssignmentRole


@strawberry.input
class AssignUserInput:
    user_id: UUID
    role: FulfillmentAssignmentRole
