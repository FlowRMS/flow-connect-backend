import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.graphql.organizations.models.remote_org import OrgsBase


class RemoteConnection(OrgsBase):
    __tablename__ = "connections"
    __table_args__ = {"schema": "subscription"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    requester_org_id: Mapped[uuid.UUID] = mapped_column()
    target_org_id: Mapped[uuid.UUID] = mapped_column()
    status: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()
