"""SQLAlchemy ORM model for PreOpportunityBalance entity."""

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel

if TYPE_CHECKING:
    from app.graphql.pre_opportunities.models.pre_opportunity_model import (
        PreOpportunity,
    )


class PreOpportunityBalance(CrmBaseModel, kw_only=True):
    """
    Read-only balance entity for pre-opportunities.

    This entity stores calculated totals and is automatically updated
    when pre-opportunity details change.
    """

    __tablename__ = "pre_opportunity_balances"

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, server_default="0"
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, server_default="0"
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, server_default="0"
    )
    discount: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, server_default="0"
    )
    discount_rate: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=2), nullable=False, server_default="0"
    )

    # Back-reference to parent (one-to-one)
    pre_opportunity: Mapped["PreOpportunity"] = relationship(
        back_populates="balance", init=False
    )
