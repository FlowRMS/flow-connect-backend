from uuid import UUID

import strawberry
from commons.db.v6.crm.jobs import JobCompanyRole


@strawberry.input
class AddCompanyToJobInput:
    job_id: UUID
    company_id: UUID
    role: JobCompanyRole


@strawberry.input
class RemoveCompanyFromJobInput:
    job_id: UUID
    company_id: UUID
    role: JobCompanyRole
