"""GraphQL response type for contact related entities."""

import strawberry

from app.graphql.companies.strawberry.company_response import CompanyResponse


@strawberry.type
class ContactRelatedEntitiesResponse:
    """Response containing all entities related to a contact."""

    companies: list[CompanyResponse]
