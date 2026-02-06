import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.graphql.organizations.models.remote_org import OrgsBase


class RemoteTenant(OrgsBase):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "subscription"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    org_id: Mapped[uuid.UUID] = mapped_column()
    is_active: Mapped[bool | None] = mapped_column()
    deleted_at: Mapped[datetime | None] = mapped_column()
