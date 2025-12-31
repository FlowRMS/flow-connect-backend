from datetime import date
from decimal import Decimal

import strawberry
from commons.db.v6.commission.orders import OrderHeaderStatus, OrderStatus, OrderType

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="OrderLandingPage")
class OrderLandingPageResponse(LandingPageInterfaceBase):
    order_number: str
    status: OrderStatus
    header_status: OrderHeaderStatus
    order_type: OrderType
    entity_date: date
    due_date: date
    total: Decimal
    published: bool
    factory_name: str
    job_name: str | None
    sold_to_customer_name: str
