from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.fulfillment import (
    FulfillmentActivity,
    FulfillmentActivityType,
    FulfillmentAssignment,
    FulfillmentAssignmentRole,
    FulfillmentOrder,
)

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.fulfillment.repositories import (
    FulfillmentActivityRepository,
    FulfillmentAssignmentRepository,
    FulfillmentOrderRepository,
)


class FulfillmentAssignmentService:
    def __init__(
        self,
        order_repository: FulfillmentOrderRepository,
        assignment_repository: FulfillmentAssignmentRepository,
        activity_repository: FulfillmentActivityRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.order_repository = order_repository
        self.assignment_repository = assignment_repository
        self.activity_repository = activity_repository
        self.auth_info = auth_info

    async def add_assignment(
        self,
        fulfillment_order_id: UUID,
        user_id: UUID,
        role: FulfillmentAssignmentRole,
    ) -> FulfillmentOrder:
        """Add a user assignment to a fulfillment order."""
        _ = await self._get_order_or_raise(fulfillment_order_id)

        # Check if assignment already exists
        existing = await self.assignment_repository.get_by_order_and_user(
            fulfillment_order_id, user_id
        )
        if existing:
            # Update role if different
            if existing.role != role:
                existing.role = role
                _ = await self.assignment_repository.update(existing)
                _ = await self._log_activity(
                    fulfillment_order_id,
                    FulfillmentActivityType.ASSIGNMENT_ADDED,
                    f"Assignment role updated to {role.name}",
                    {"user_id": str(user_id), "role": role.name},
                )
            order = await self.order_repository.get_with_relations(fulfillment_order_id)
            if not order:
                raise NotFoundError(
                    f"Fulfillment order {fulfillment_order_id} not found"
                )
            return order

        # Create new assignment
        assignment = FulfillmentAssignment()
        assignment.fulfillment_order_id = fulfillment_order_id
        assignment.user_id = user_id
        assignment.role = role
        assignment.created_by_id = self.auth_info.flow_user_id

        _ = await self.assignment_repository.create(assignment)

        _ = await self._log_activity(
            fulfillment_order_id,
            FulfillmentActivityType.ASSIGNMENT_ADDED,
            f"User assigned as {role.name}",
            {"user_id": str(user_id), "role": role.name},
        )

        order = await self.order_repository.get_with_relations(fulfillment_order_id)
        if not order:
            raise NotFoundError(f"Fulfillment order {fulfillment_order_id} not found")
        return order

    async def remove_assignment(
        self,
        assignment_id: UUID,
    ) -> FulfillmentOrder:
        """Remove an assignment from a fulfillment order."""
        assignment = await self.assignment_repository.get_by_id(assignment_id)
        if not assignment:
            raise NotFoundError(f"Assignment {assignment_id} not found")

        fulfillment_order_id = assignment.fulfillment_order_id
        user_id = assignment.user_id
        role = assignment.role

        _ = await self.assignment_repository.delete(assignment_id)

        _ = await self._log_activity(
            fulfillment_order_id,
            FulfillmentActivityType.ASSIGNMENT_REMOVED,
            f"User removed from {role.name} assignment",
            {"user_id": str(user_id), "role": role.name},
        )

        order = await self.order_repository.get_with_relations(fulfillment_order_id)
        if not order:
            raise NotFoundError(f"Fulfillment order {fulfillment_order_id} not found")
        return order

    async def _get_order_or_raise(self, order_id: UUID) -> FulfillmentOrder:
        order = await self.order_repository.get_with_relations(order_id)
        if not order:
            raise NotFoundError(f"Fulfillment order {order_id} not found")
        return order

    async def _log_activity(
        self,
        order_id: UUID,
        activity_type: FulfillmentActivityType,
        content: str,
        metadata: dict | None = None,
    ) -> FulfillmentActivity:
        activity = FulfillmentActivity(
            activity_type=activity_type,
            content=content,
            activity_metadata=metadata,
        )
        activity.fulfillment_order_id = order_id
        activity.created_by_id = self.auth_info.flow_user_id
        return await self.activity_repository.create(activity)
