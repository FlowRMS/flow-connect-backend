from datetime import datetime

from pydantic import BaseModel, Field


class WorkOSDomain(BaseModel):
    id: str
    domain: str
    state: str
    object: str = "organization_domain"
    organization_id: str
    verification_strategy: str | None = None
    verification_token: str | None = None


class WorkOSOrganizationData(BaseModel):
    id: str
    name: str
    object: str = "organization"
    external_id: str | None = None
    domains: list[WorkOSDomain] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class WorkOSEvent(BaseModel):
    id: str
    event: str
    created_at: datetime
    data: WorkOSOrganizationData
