from datetime import date
from decimal import Decimal

import strawberry
from commons.db.v6.common.creation_type import CreationType

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="OrderAcknowledgementLandingPage")
class OrderAcknowledgementLandingPageResponse(LandingPageInterfaceBase):
    order_acknowledgement_number: str
    entity_date: date
    quantity: Decimal
    ship_date: date | None
    creation_type: CreationType
    order_number: str
    order_entity_date: date
    sold_to_customer_name: str
    factory_name: str
    product_name: str | None
    item_number: int
