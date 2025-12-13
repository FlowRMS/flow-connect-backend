import uuid

from commons.db.models import User
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import HasCreatedAt, HasCreatedBy, LocalBaseModel


class CustomerV2(LocalBaseModel, HasCreatedBy, HasCreatedAt):
    __tablename__ = "customers"

    company_name: Mapped[str]
    published: Mapped[bool] = mapped_column(default=False)
    is_parent: Mapped[bool] = mapped_column(default=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("customers.id"), nullable=True, default=None
    )
    contact_email: Mapped[str | None] = mapped_column(default=None)
    contact_number: Mapped[str | None] = mapped_column(default=None)
    customer_branch_id: Mapped[uuid.UUID | None] = mapped_column(default=None)
    customer_territory_id: Mapped[uuid.UUID | None] = mapped_column(default=None)
    logo_url: Mapped[str | None] = mapped_column(default=None)
    inside_rep_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(User.id), nullable=True, default=None
    )

    type: Mapped[str | None] = mapped_column(default=None)

    created_by: Mapped["User"] = relationship(
        lazy="joined", init=False, foreign_keys="CustomerV2.created_by_id"
    )
    inside_rep: Mapped["User | None"] = relationship(
        lazy="joined", init=False, foreign_keys=[inside_rep_id]
    )
