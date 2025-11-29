"""SQLAlchemy ORM model for CompanyAddress entity."""

from uuid import UUID

from commons.db.int_enum import IntEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasCreatedAt, HasCreatedBy
from app.graphql.addresses.models.address_type import AddressType
from app.graphql.companies.models.company_model import Company


class CompanyAddress(CrmBaseModel, HasCreatedAt, HasCreatedBy, kw_only=True):
    """
    CompanyAddress entity representing an address in the CRM system.

    Addresses are associated with companies and can be of different types
    (BILLING, SHIPPING, OTHER).
    """

    __tablename__ = "addresses"

    company_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(Company.id),
        nullable=False,
    )
    address_type: Mapped[AddressType] = mapped_column(
        IntEnum(AddressType), nullable=False
    )

    address_line_1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    zip_code: Mapped[str | None] = mapped_column(String(20), nullable=True)

    company: Mapped[Company] = relationship(
        back_populates="addresses", init=False, lazy="noload"
    )

    def __repr__(self) -> str:
        """String representation of the CompanyAddress."""
        return f"<CompanyAddress(id={self.id}, company_id={self.company_id}, type='{self.address_type}')>"
