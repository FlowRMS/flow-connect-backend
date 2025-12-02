"""SQLAlchemy ORM model for Company entity."""

from typing import TYPE_CHECKING
from uuid import UUID

from commons.db.int_enum import IntEnum
from commons.db.models import User
from sqlalchemy import ARRAY, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasCreatedAt, HasCreatedBy
from app.graphql.companies.models.company_type import CompanyType

if TYPE_CHECKING:
    from app.graphql.addresses.models.address_model import CompanyAddress
    from app.graphql.contacts.models.contact_model import Contact


class Company(CrmBaseModel, HasCreatedAt, HasCreatedBy, kw_only=True):
    """
    Company entity representing a company in the CRM system.

    Companies can be of type CUSTOMER or MANUFACTURER.
    """

    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_source_type: Mapped[CompanyType] = mapped_column(
        IntEnum(CompanyType), nullable=False
    )

    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    parent_company_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    addresses: Mapped[list["CompanyAddress"]] = relationship(
        init=False, back_populates="company", cascade="all, delete-orphan"
    )
    contacts: Mapped[list["Contact"]] = relationship(
        init=False,
        back_populates="company",
    )
    created_by: Mapped[User] = relationship(init=False, lazy="joined")

    def __repr__(self) -> str:
        """String representation of the Company."""
        return f"<Company(id={self.id}, name='{self.name}', type='{self.company_source_type}')>"
