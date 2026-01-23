from app.graphql.v2.core.deliveries.mutations.deliveries_mutations import (
    DeliveriesMutations,
)
from app.graphql.v2.core.deliveries.mutations.delivery_assignees_mutations import (
    DeliveryAssigneesMutations,
)
from app.graphql.v2.core.deliveries.mutations.delivery_documents_mutations import (
    DeliveryDocumentsMutations,
)
from app.graphql.v2.core.deliveries.mutations.delivery_issues_mutations import (
    DeliveryIssuesMutations,
)
from app.graphql.v2.core.deliveries.mutations.delivery_item_receipts_mutations import (
    DeliveryItemReceiptsMutations,
)
from app.graphql.v2.core.deliveries.mutations.delivery_items_mutations import (
    DeliveryItemsMutations,
)
from app.graphql.v2.core.deliveries.mutations.delivery_status_history_mutations import (
    DeliveryStatusHistoryMutations,
)
from app.graphql.v2.core.deliveries.mutations.recurring_shipments_mutations import (
    RecurringShipmentsMutations,
)

__all__ = [
    "DeliveriesMutations",
    "DeliveryAssigneesMutations",
    "DeliveryDocumentsMutations",
    "DeliveryItemReceiptsMutations",
    "DeliveryItemsMutations",
    "DeliveryIssuesMutations",
    "DeliveryStatusHistoryMutations",
    "RecurringShipmentsMutations",
]
