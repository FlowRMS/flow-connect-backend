import strawberry

from app.graphql.companies.strawberry.company_response import CompanyLiteResponse
from app.graphql.v2.core.customers.strawberry.customer_response import (
    CustomerLiteResponse,
)


@strawberry.type
class ContactRelatedEntitiesResponse:
    companies: list[CompanyLiteResponse]
    customers: list[CustomerLiteResponse]
