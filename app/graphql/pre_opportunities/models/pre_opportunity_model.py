"""SQLAlchemy ORM model for PreOpportunity entity."""

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from commons.db.int_enum import IntEnum
from commons.db.models import Customer, User
from sqlalchemy import ARRAY, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasCreatedAt, HasCreatedBy
from app.graphql.jobs.models.jobs_model import Job
from app.graphql.pre_opportunities.models.pre_opportunity_balance_model import (
    PreOpportunityBalance,
)
from app.graphql.pre_opportunities.models.pre_opportunity_status import (
    PreOpportunityStatus,
)

if TYPE_CHECKING:
    from app.graphql.pre_opportunities.models.pre_opportunity_detail_model import (
        PreOpportunityDetail,
    )


class PreOpportunity(CrmBaseModel, HasCreatedAt, HasCreatedBy, kw_only=True):
    """
    PreOpportunity entity representing a potential sales opportunity.

    Tracks opportunities from initial quote through conversion or rejection.
    """

    __tablename__ = "pre_opportunities"

    status: Mapped[PreOpportunityStatus] = mapped_column(
        IntEnum(PreOpportunityStatus), nullable=False
    )
    entity_number: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_date: Mapped[date] = mapped_column(Date, nullable=False)

    exp_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    revise_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    accept_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Foreign keys - Customer references (from core schema)
    sold_to_customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(Customer.id),
        nullable=False,
    )
    sold_to_customer_address_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    bill_to_customer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(Customer.id),
        nullable=True,
    )
    bill_to_customer_address_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )

    # Foreign keys - Job reference (from CRM schema)
    job_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(Job.id),
        nullable=True,
    )

    # Foreign keys - Balance (one-to-one)
    balance_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(PreOpportunityBalance.id),
        nullable=False,
        unique=True,
        init=False,
    )

    # Optional fields
    payment_terms: Mapped[str | None] = mapped_column(String(255), nullable=True)
    customer_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    freight_terms: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    # Relationships
    balance: Mapped["PreOpportunityBalance"] = relationship(
        back_populates="pre_opportunity",
        init=False,
        lazy="joined",
        # cascade="all, delete-orphan",
    )

    details: Mapped[list["PreOpportunityDetail"]] = relationship(
        default_factory=list,
        back_populates="pre_opportunity",
        lazy="selectin",
        cascade="all, delete, delete-orphan",
    )

    job: Mapped["Job | None"] = relationship(init=False, lazy="joined")
    created_by: Mapped[User] = relationship(init=False, lazy="joined")

    def __repr__(self) -> str:
        """String representation of the PreOpportunity."""
        return f"<PreOpportunity(id={self.id}, entity_number='{self.entity_number}')>"
