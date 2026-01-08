from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class EntityMapping:
    factory_id: UUID | None = None
    sold_to_customer_id: UUID | None = None
    bill_to_customer_id: UUID | None = None
    order_id: UUID | None = None
    invoice_id: UUID | None = None
    credit_id: UUID | None = None
    adjustment_id: UUID | None = None
    products: dict[int, UUID] = field(default_factory=dict)
    end_users: dict[int, UUID] = field(default_factory=dict)
    skipped_product_indices: set[int] = field(default_factory=set)
    skipped_order_indices: set[int] = field(default_factory=set)
    skipped_invoice_indices: set[int] = field(default_factory=set)

    def get_product_id(self, flow_index: int | None) -> UUID | None:
        if flow_index is None:
            return None
        return self.products.get(flow_index)

    def get_end_user_id(
        self,
        flow_index: int | None,
        *,
        fallback: UUID | None = None,
    ) -> UUID | None:
        if flow_index is not None:
            end_user = self.end_users.get(flow_index)
            if end_user:
                return end_user
        return fallback or self.sold_to_customer_id
