"""GraphQL response type for job related entities."""

import strawberry

from app.graphql.companies.strawberry.company_response import CompanyResponse
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.pre_opportunities.strawberry.pre_opportunity_lite_response import (
    PreOpportunityLiteResponse,
)


@strawberry.type
class JobRelatedEntitiesResponse:
    """Response containing all entities related to a job."""

    pre_opportunities: list[PreOpportunityLiteResponse]
    contacts: list[ContactResponse]
    companies: list[CompanyResponse]
