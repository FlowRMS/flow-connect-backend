from app.graphql.jobs.models.job_status import JobStatus
from app.graphql.jobs.models.jobs_model import Job
from app.graphql.companies.models.company_model import Company
from app.graphql.addresses.models.address_model import Address
# from commons.db.models.base import Base
from app.core.db.base import BaseModel as Base

__all__ = [
    "Base",
    "Job",
    "JobStatus",
    "Company",
    "Address",
]
