"""GraphQL response type for task related entities."""

import strawberry

from app.graphql.checks.strawberry.check_response import CheckResponse
from app.graphql.companies.strawberry.company_response import CompanyResponse
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.customers.strawberry.customer_response import CustomerResponse
from app.graphql.factories.strawberry.factory_response import FactoryResponse
from app.graphql.invoices.strawberry.invoice_response import InvoiceResponse
from app.graphql.jobs.strawberry.job_response import JobType
from app.graphql.notes.strawberry.note_response import NoteType
from app.graphql.orders.strawberry.order_response import OrderResponse
from app.graphql.pre_opportunities.strawberry.pre_opportunity_lite_response import (
    PreOpportunityLiteResponse,
)
from app.graphql.products.strawberry.product_response import ProductResponse
from app.graphql.quotes.strawberry.quote_response import QuoteResponse


@strawberry.type
class TaskRelatedEntitiesResponse:
    """Response containing all entities related to a task."""

    jobs: list[JobType]
    contacts: list[ContactResponse]
    companies: list[CompanyResponse]
    notes: list[NoteType]
    pre_opportunities: list[PreOpportunityLiteResponse]
    quotes: list[QuoteResponse]
    orders: list[OrderResponse]
    invoices: list[InvoiceResponse]
    checks: list[CheckResponse]
    factories: list[FactoryResponse]
    products: list[ProductResponse]
    customers: list[CustomerResponse]
