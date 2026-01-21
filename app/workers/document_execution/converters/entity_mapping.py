from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class EntityMapping:
    factory_id: UUID | None = None
    sold_to_customer_id: UUID | None = None
    bill_to_customer_id: UUID | None = None
    orders: dict[int, UUID] = field(default_factory=dict)
    invoices: dict[int, UUID] = field(default_factory=dict)
    credits: dict[int, UUID] = field(default_factory=dict)
    adjustments: dict[int, UUID] = field(default_factory=dict)
    products: dict[int, UUID] = field(default_factory=dict)
    end_users: dict[int, UUID] = field(default_factory=dict)
    skipped_product_indices: set[int] = field(default_factory=set)
    skipped_order_indices: set[int] = field(default_factory=set)
    skipped_invoice_indices: set[int] = field(default_factory=set)

    def get_product_id(self, flow_detail_index: int | None) -> UUID | None:
        if flow_detail_index is None:
            return None
        return self.products.get(flow_detail_index)

    def get_end_user_id(
        self,
        flow_detail_index: int | None,
        *,
        fallback: UUID | None = None,
    ) -> UUID | None:
        if flow_detail_index is not None:
            end_user = self.end_users.get(flow_detail_index)
            if end_user:
                return end_user
        return fallback or self.sold_to_customer_id

    def get_order_id(self, flow_detail_index: int | None) -> UUID | None:
        if flow_detail_index is None:
            return self.orders.get(0)
        return self.orders.get(flow_detail_index)

    def get_invoice_id(self, flow_detail_index: int | None) -> UUID | None:
        if flow_detail_index is None:
            return None
        return self.invoices.get(flow_detail_index)

    def get_credit_id(self, flow_detail_index: int | None) -> UUID | None:
        if flow_detail_index is None:
            return None
        return self.credits.get(flow_detail_index)

    def get_adjustment_id(self, flow_detail_index: int | None) -> UUID | None:
        if flow_detail_index is None:
            return None
        return self.adjustments.get(flow_detail_index)
