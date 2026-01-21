import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.jobs.services.job_company_link_service import JobCompanyLinkService
from app.graphql.jobs.strawberry.job_company_link_input import (
    AddCompanyToJobInput,
    RemoveCompanyFromJobInput,
)
from app.graphql.jobs.strawberry.job_company_link_response import JobCompanyLinkResponse


@strawberry.type
class JobCompanyLinkMutations:
    @strawberry.mutation
    @inject
    async def add_company_to_job(
        self,
        input: AddCompanyToJobInput,
        service: Injected[JobCompanyLinkService],
    ) -> JobCompanyLinkResponse:
        link = await service.add_company_to_job(
            job_id=input.job_id,
            company_id=input.company_id,
            role=input.role,
        )
        return JobCompanyLinkResponse.from_orm_model(link)

    @strawberry.mutation
    @inject
    async def remove_company_from_job(
        self,
        input: RemoveCompanyFromJobInput,
        service: Injected[JobCompanyLinkService],
    ) -> bool:
        return await service.remove_company_from_job(
            job_id=input.job_id,
            company_id=input.company_id,
            role=input.role,
        )
