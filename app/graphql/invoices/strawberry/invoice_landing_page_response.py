from datetime import date
from decimal import Decimal

import strawberry
from commons.db.v6.commission.invoices.invoice import InvoiceStatus

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="InvoiceLandingPage")
class InvoiceLandingPageResponse(LandingPageInterfaceBase):
    invoice_number: str
    status: InvoiceStatus
    entity_date: date
    due_date: date | None
    total: Decimal
    published: bool
    locked: bool
    order_id: str
    order_number: str
    factory_name: str
