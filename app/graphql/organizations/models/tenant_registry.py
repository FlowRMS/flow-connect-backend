import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.graphql.organizations.models.remote_org import OrgsBase


class TenantRegistry(OrgsBase):
    __tablename__ = "tenant_registry"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    org_id: Mapped[uuid.UUID] = mapped_column()
    status: Mapped[str] = mapped_column(String(20))
