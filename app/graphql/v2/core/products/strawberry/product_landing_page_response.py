from decimal import Decimal

import strawberry

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="ProductLandingPage")
class ProductLandingPageResponse(LandingPageInterfaceBase):
    factory_part_number: str
    unit_price: Decimal
    default_commission_rate: Decimal | None
    published: bool
    approval_needed: bool
    description: str | None
    factory_title: str
    category_title: str | None
    uom_title: str | None
    tags: list[str] | None
