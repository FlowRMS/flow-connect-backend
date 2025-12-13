"""GraphQL response type for job related entities."""

import strawberry

from app.graphql.checks.strawberry.check_response import CheckResponse
from app.graphql.companies.strawberry.company_response import CompanyResponse
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.core.customers.strawberry.customer_response import CustomerResponse
from app.graphql.core.factories.strawberry.factory_response import FactoryResponse
from app.graphql.core.products.strawberry.product_response import ProductResponse
from app.graphql.invoices.strawberry.invoice_response import InvoiceResponse
from app.graphql.orders.strawberry.order_response import OrderResponse
from app.graphql.pre_opportunities.strawberry.pre_opportunity_lite_response import (
    PreOpportunityLiteResponse,
)
from app.graphql.quotes.strawberry.quote_response import QuoteResponse


@strawberry.type
class JobRelatedEntitiesResponse:
    """Response containing all entities related to a job."""

    pre_opportunities: list[PreOpportunityLiteResponse]
    contacts: list[ContactResponse]
    companies: list[CompanyResponse]
    quotes: list[QuoteResponse]
    orders: list[OrderResponse]
    invoices: list[InvoiceResponse]
    checks: list[CheckResponse]
    factories: list[FactoryResponse]
    products: list[ProductResponse]
    customers: list[CustomerResponse]
