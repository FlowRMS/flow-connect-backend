import uuid
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.graphql.organizations.models.remote_org import OrgsBase


class RemoteAppRole(OrgsBase):
    __tablename__ = "ar_app_roles"
    __table_args__ = {"schema": "subscription"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    role_key: Mapped[str] = mapped_column()
    display_name: Mapped[str | None] = mapped_column()
    description: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()


class RemoteUserAppRole(OrgsBase):
    __tablename__ = "ar_user_app_roles"
    __table_args__ = {"schema": "subscription"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column()
    app_role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("subscription.ar_app_roles.id", ondelete="CASCADE")
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()

    app_role: Mapped[RemoteAppRole] = relationship()
