from typing import Any, Self
from uuid import UUID

import strawberry
from commons.db.v6.rbac.rbac_privilege_option_enum import RbacPrivilegeOptionEnum
from commons.graphql.filter_types import Filter
from commons.graphql.order_by_types import OrderBy
from commons.graphql.pagination import get_pagination_window as _get_pagination_window
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.adjustments.strawberry.adjustment_landing_page_response import (
    AdjustmentLandingPageResponse,
)
from app.graphql.campaigns.strawberry.campaign_landing_page_response import (
    CampaignLandingPageResponse,
)
from app.graphql.checks.strawberry.check_landing_page_response import (
    CheckLandingPageResponse,
)
from app.graphql.companies.strawberry.company_landing_page_response import (
    CompanyLandingPageResponse,
)
from app.graphql.contacts.strawberry.contact_landing_page_response import (
    ContactLandingPageResponse,
)
from app.graphql.credits.strawberry.credit_landing_page_response import (
    CreditLandingPageResponse,
)
from app.graphql.documents.strawberry.pending_document_landing_page_response import (
    PendingDocumentLandingPageResponse,
)
from app.graphql.invoices.strawberry.invoice_landing_page_response import (
    InvoiceLandingPageResponse,
)
from app.graphql.jobs.strawberry.job_landing_page_response import JobLandingPageResponse
from app.graphql.notes.strawberry.note_landing_page_response import (
    NoteLandingPageResponse,
)
from app.graphql.orders.strawberry.order_acknowledgement_landing_page_response import (
    OrderAcknowledgementLandingPageResponse,
)
from app.graphql.orders.strawberry.order_landing_page_response import (
    OrderLandingPageResponse,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_landing_page_response import (
    PreOpportunityLandingPageResponse,
)
from app.graphql.quotes.strawberry.quote_landing_page_response import (
    QuoteLandingPageResponse,
)
from app.graphql.tasks.strawberry.task_landing_page_response import (
    TaskLandingPageResponse,
)
from app.graphql.v2.core.customers.strawberry.customer_landing_page_response import (
    CustomerLandingPageResponse,
)
from app.graphql.v2.core.factories.strawberry.factory_landing_page_response import (
    FactoryLandingPageResponse,
)
from app.graphql.v2.core.products.strawberry.product_landing_page_response import (
    ProductLandingPageResponse,
)
from app.graphql.v2.files.strawberry.file_landing_page_response import (
    FileLandingPageResponse,
)

LandingRecord = strawberry.union(
    name="LandingRecord",
    types=[
        JobLandingPageResponse,
        CompanyLandingPageResponse,
        ContactLandingPageResponse,
        PreOpportunityLandingPageResponse,
        NoteLandingPageResponse,
        TaskLandingPageResponse,
        CampaignLandingPageResponse,
        CustomerLandingPageResponse,
        FactoryLandingPageResponse,
        ProductLandingPageResponse,
        QuoteLandingPageResponse,
        OrderLandingPageResponse,
        FileLandingPageResponse,
        InvoiceLandingPageResponse,
        CreditLandingPageResponse,
        AdjustmentLandingPageResponse,
        CheckLandingPageResponse,
        OrderAcknowledgementLandingPageResponse,
        PendingDocumentLandingPageResponse,
    ],
)


@strawberry.type(name="GenericLandingPage")
class PaginatedLandingPageInterface:
    """Generic paginated landing page response with records and total count."""

    records: list[LandingRecord]
    total: int

    @classmethod
    async def get_pagination_window(
        cls,
        session: AsyncSession,
        stmt: Select[Any],
        record_type: type[Any],
        record_type_gql: type[Any],
        filters: list[Filter] | None = None,
        order_by: OrderBy | list[OrderBy] | None = None,
        limit: int | None = 10,
        offset: int | None = 0,
        rbac_option: RbacPrivilegeOptionEnum | None = None,
        user_id: UUID | None = None,
    ) -> Self:
        records, total = await _get_pagination_window(
            session=session,
            query=stmt,
            record_type=record_type,
            record_type_gql=record_type_gql,
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
            rbac_option=rbac_option,
            user_id=user_id,
        )

        return cls(records=records, total=total)
