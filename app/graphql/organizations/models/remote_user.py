import uuid
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.graphql.organizations.models.remote_org import OrgsBase


class RemoteUser(OrgsBase):
    __tablename__ = "users"
    __table_args__ = {"schema": "subscription"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    workos_user_id: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    org_primary_id: Mapped[uuid.UUID | None] = mapped_column()
    first_name: Mapped[str | None] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()
    deleted_at: Mapped[datetime | None] = mapped_column()
