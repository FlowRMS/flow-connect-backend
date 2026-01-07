import strawberry

from app.graphql.checks.strawberry.check_response import CheckResponse
from app.graphql.invoices.strawberry.invoice_response import InvoiceResponse
from app.graphql.orders.strawberry.order_response import OrderResponse
from app.graphql.pre_opportunities.strawberry.pre_opportunity_response import (
    PreOpportunityResponse,
)
from app.graphql.quotes.strawberry.quote_response import QuoteResponse

EntityResponse = strawberry.union(
    name="EntityResponse",
    types=[
        PreOpportunityResponse,
        QuoteResponse,
        OrderResponse,
        InvoiceResponse,
        CheckResponse,
    ],
)
