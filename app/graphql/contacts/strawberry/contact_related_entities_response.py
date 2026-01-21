import strawberry

from app.graphql.companies.strawberry.company_response import CompanyLiteResponse


@strawberry.type
class ContactRelatedEntitiesResponse:
    companies: list[CompanyLiteResponse]
