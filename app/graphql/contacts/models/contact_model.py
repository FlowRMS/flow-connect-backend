"""SQLAlchemy ORM model for Contact entity."""

from uuid import UUID

from sqlalchemy import ARRAY, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasCreatedAt, HasCreatedBy
from app.graphql.companies.models.company_model import Company


class Contact(CrmBaseModel, HasCreatedAt, HasCreatedBy, kw_only=True):
    """
    Contact entity representing a contact in the CRM system.

    Contacts are associated with companies and store personal/professional information.
    """

    __tablename__ = "contacts"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    territory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    company_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(Company.id),
        nullable=True,
    )
    company: Mapped[Company | None] = relationship(
        init=False, back_populates="contacts"
    )

    def __repr__(self) -> str:
        """String representation of the Contact."""
        return f"<Contact(id={self.id}, name='{self.first_name} {self.last_name}')>"
