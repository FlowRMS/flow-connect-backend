"""GraphQL response type for note related entities."""

import strawberry

from app.graphql.companies.strawberry.company_response import CompanyResponse
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.jobs.strawberry.job_response import JobType
from app.graphql.pre_opportunities.strawberry.pre_opportunity_lite_response import (
    PreOpportunityLiteResponse,
)
from app.graphql.tasks.strawberry.task_response import TaskType


@strawberry.type
class NoteRelatedEntitiesResponse:
    """Response containing all entities related to a note."""

    jobs: list[JobType]
    tasks: list[TaskType]
    contacts: list[ContactResponse]
    companies: list[CompanyResponse]
    pre_opportunities: list[PreOpportunityLiteResponse]
