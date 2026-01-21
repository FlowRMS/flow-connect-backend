from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.jobs import JobCompanyLink, JobCompanyRole

from app.core.db.adapters.dto import DTOMixin
from app.graphql.companies.strawberry.company_response import CompanyLiteResponse


@strawberry.type
class JobCompanyLinkResponse(DTOMixin[JobCompanyLink]):
    _instance: strawberry.Private[JobCompanyLink]
    id: UUID
    job_id: UUID
    company_id: UUID
    role: JobCompanyRole
    created_at: datetime

    @strawberry.field
    def company(self) -> CompanyLiteResponse:
        return CompanyLiteResponse.from_orm_model(self._instance.company)

    @classmethod
    def from_orm_model(cls, model: JobCompanyLink) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            job_id=model.job_id,
            company_id=model.company_id,
            role=model.role,
            created_at=model.created_at,
        )
