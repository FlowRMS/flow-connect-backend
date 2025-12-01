"""GraphQL response type for task related entities."""

import strawberry

from app.graphql.companies.strawberry.company_response import CompanyResponse
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.jobs.strawberry.job_response import JobType
from app.graphql.notes.strawberry.note_response import NoteType


@strawberry.type
class TaskRelatedEntitiesResponse:
    """Response containing all entities related to a task."""

    jobs: list[JobType]
    contacts: list[ContactResponse]
    companies: list[CompanyResponse]
    notes: list[NoteType]
