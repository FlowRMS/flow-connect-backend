from uuid import UUID

import strawberry

from app.graphql.checks.strawberry.check_response import CheckLiteResponse
from app.graphql.common.landing_source_type import LandingSourceType
from app.graphql.companies.strawberry.company_response import CompanyLiteResponse
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.invoices.strawberry.invoice_response import InvoiceLiteResponse
from app.graphql.jobs.strawberry.job_response import JobLiteType
from app.graphql.notes.strawberry.note_response import NoteType
from app.graphql.orders.strawberry.order_lite_response import OrderLiteResponse
from app.graphql.pre_opportunities.strawberry.pre_opportunity_lite_response import (
    PreOpportunityLiteResponse,
)
from app.graphql.quotes.strawberry.quote_lite_response import QuoteLiteResponse
from app.graphql.statements.strawberry.statement_lite_response import (
    StatementLiteResponse,
)
from app.graphql.tasks.strawberry.task_response import TaskType
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.products.strawberry.product_response import ProductLiteResponse


@strawberry.type
class RelatedEntitiesResponse:
    source_type: LandingSourceType
    source_entity_id: UUID
    jobs: list[JobLiteType] | None = None
    tasks: list[TaskType] | None = None
    notes: list[NoteType] | None = None
    contacts: list[ContactResponse] | None = None
    companies: list[CompanyLiteResponse] | None = None
    pre_opportunities: list[PreOpportunityLiteResponse] | None = None
    quotes: list[QuoteLiteResponse] | None = None
    orders: list[OrderLiteResponse] | None = None
    invoices: list[InvoiceLiteResponse] | None = None
    checks: list[CheckLiteResponse] | None = None
    factories: list[FactoryLiteResponse] | None = None
    products: list[ProductLiteResponse] | None = None
    customers: list[CustomerLiteResponse] | None = None
    statements: list[StatementLiteResponse] | None = None
