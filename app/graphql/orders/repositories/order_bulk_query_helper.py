from typing import Any
from uuid import UUID

from commons.db.v6.commission.orders import Order, OrderDetail
from sqlalchemy import Select, or_, select
from sqlalchemy.orm import joinedload, lazyload

ORDER_WITH_DETAILS_OPTIONS = [
    lazyload("*"),
    joinedload(Order.details),
    joinedload(Order.details).joinedload(OrderDetail.invoices),
    joinedload(Order.details).joinedload(OrderDetail.end_user),
    joinedload(Order.details).joinedload(OrderDetail.product),
    joinedload(Order.details).joinedload(OrderDetail.outside_split_rates),
    joinedload(Order.details).joinedload(OrderDetail.inside_split_rates),
    joinedload(Order.details).joinedload(OrderDetail.uom),
    joinedload(Order.balance),
]


def build_find_order_by_number_customer_with_details_stmt(
    order_number: str, customer_id: UUID
) -> Select[Any]:
    return (
        select(Order)
        .options(*ORDER_WITH_DETAILS_OPTIONS)
        .where(
            Order.order_number == order_number,
            Order.sold_to_customer_id == customer_id,
        )
    )


def build_find_orders_by_number_customer_pairs_stmt(
    order_customer_pairs: list[tuple[str, UUID]],
) -> Select[Any]:
    if not order_customer_pairs:
        return select(Order).where(Order.id.is_(None))

    conditions = [
        (Order.order_number == order_num) & (Order.sold_to_customer_id == cust_id)
        for order_num, cust_id in order_customer_pairs
    ]
    return select(Order).options(*ORDER_WITH_DETAILS_OPTIONS).where(or_(*conditions))
