import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import HasCreatedAt, HasCreatedByV2, LocalBaseModel
from app.graphql.core.factories.models.enums import (
    CommissionPolicyEnum,
    FreightDiscountTypeEnum,
)
from app.graphql.core.users.models.user import UserV2


class FactoryV2(LocalBaseModel, HasCreatedByV2, HasCreatedAt):
    __tablename__ = "factories"

    title: Mapped[str]
    published: Mapped[bool] = mapped_column(default=False)
    account_number: Mapped[str | None] = mapped_column(default=None)
    email: Mapped[str | None] = mapped_column(default=None)
    phone: Mapped[str | None] = mapped_column(default=None)
    external_terms: Mapped[str | None] = mapped_column(default=None)
    additional_information: Mapped[str | None] = mapped_column(default=None)
    freight_terms: Mapped[str | None] = mapped_column(default=None)
    freight_discount_type: Mapped[int] = mapped_column(
        default=int(FreightDiscountTypeEnum.NONE)
    )
    lead_time: Mapped[str | None] = mapped_column(default=None)
    payment_terms: Mapped[str | None] = mapped_column(default=None)
    commission_rate: Mapped[Decimal | None] = mapped_column(default=None)
    commission_discount_rate: Mapped[Decimal | None] = mapped_column(default=None)
    overall_discount_rate: Mapped[Decimal | None] = mapped_column(default=None)
    logo_url: Mapped[str | None] = mapped_column(default=None)
    inside_rep_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(UserV2.id), nullable=True, default=None
    )
    external_payment_terms: Mapped[str | None] = mapped_column(default=None)
    commission_policy: Mapped[int] = mapped_column(
        default=int(CommissionPolicyEnum.STANDARD)
    )
    direct_commission_allowed: Mapped[bool] = mapped_column(default=True)

    created_by: Mapped[UserV2] = relationship(
        lazy="joined", init=False, foreign_keys="FactoryV2.created_by_id"
    )
    inside_rep: Mapped[UserV2 | None] = relationship(
        lazy="joined", init=False, foreign_keys=[inside_rep_id]
    )
