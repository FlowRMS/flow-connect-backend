"""GraphQL response type for job related entities."""

import strawberry

from app.graphql.checks.strawberry.check_response import CheckLiteResponse
from app.graphql.companies.strawberry.company_response import CompanyLiteResponse
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.invoices.strawberry.invoice_response import InvoiceLiteResponse
from app.graphql.orders.strawberry.order_response import OrderLiteResponse
from app.graphql.pre_opportunities.strawberry.pre_opportunity_lite_response import (
    PreOpportunityLiteResponse,
)
from app.graphql.quotes.strawberry.quote_response import QuoteLiteResponse
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.products.strawberry.product_response import ProductLiteResponse


@strawberry.type
class JobRelatedEntitiesResponse:
    """Response containing all entities related to a job."""

    pre_opportunities: list[PreOpportunityLiteResponse]
    contacts: list[ContactResponse]
    companies: list[CompanyLiteResponse]
    quotes: list[QuoteLiteResponse]
    orders: list[OrderLiteResponse]
    invoices: list[InvoiceLiteResponse]
    checks: list[CheckLiteResponse]
    factories: list[FactoryLiteResponse]
    products: list[ProductLiteResponse]
    customers: list[CustomerLiteResponse]
