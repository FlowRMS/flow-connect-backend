"""SQLAlchemy ORM model for PreOpportunityDetail entity."""

from decimal import Decimal
from uuid import UUID

from commons.db.models.core.customer import Customer
from commons.db.models.core.product import Product
from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasPrimaryKey
from app.graphql.pre_opportunities.models.pre_opportunity_model import (
    PreOpportunity,
)


class PreOpportunityDetail(CrmBaseModel, HasPrimaryKey, kw_only=True):
    """
    Line item detail for a pre-opportunity.

    Represents individual products/services in the opportunity.
    """

    __tablename__ = "pre_opportunity_details"

    # Parent reference
    pre_opportunity_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(PreOpportunity.id),
        nullable=False,
        init=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )
    item_number: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, server_default="0"
    )
    discount_rate: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=2), nullable=False, server_default="0"
    )
    discount: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, server_default="0"
    )

    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(Product.id),
        nullable=False,
    )
    product_cpn_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True
    )
    end_user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey(Customer.id), nullable=False
    )

    lead_time: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    pre_opportunity: Mapped["PreOpportunity"] = relationship(
        back_populates="details", init=False
    )
    product: Mapped[Product] = relationship(init=False, lazy="joined")
