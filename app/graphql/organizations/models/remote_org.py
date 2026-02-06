import uuid
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class OrgsBase(DeclarativeBase):
    pass


class RemoteOrg(OrgsBase):
    __tablename__ = "orgs"
    __table_args__ = {"schema": "subscription"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    org_type: Mapped[str] = mapped_column()
    domain: Mapped[str | None] = mapped_column()
    status: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()
    deleted_at: Mapped[datetime | None] = mapped_column()

    memberships: Mapped[list["RemoteOrgMembership"]] = relationship(
        back_populates="org"
    )


class RemoteOrgMembership(OrgsBase):
    __tablename__ = "org_memberships"
    __table_args__ = {"schema": "subscription"}

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("subscription.orgs.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column()
    role: Mapped[str] = mapped_column()
    is_admin: Mapped[bool | None] = mapped_column()
    is_primary: Mapped[bool | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column()
    deleted_at: Mapped[datetime | None] = mapped_column()

    org: Mapped[RemoteOrg] = relationship(back_populates="memberships")
