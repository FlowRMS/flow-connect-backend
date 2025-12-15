import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import HasCreatedAt, HasCreatedByV2, LocalBaseModel
from app.graphql.v2.core.users.models.user import UserV2


class CustomerV2(LocalBaseModel, HasCreatedByV2, HasCreatedAt):
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
        ForeignKey(UserV2.id), nullable=True, default=None
    )

    type: Mapped[str | None] = mapped_column(default=None)

    created_by: Mapped[UserV2] = relationship(
        lazy="joined", init=False, foreign_keys="CustomerV2.created_by_id"
    )
    inside_rep: Mapped[UserV2 | None] = relationship(
        lazy="joined", init=False, foreign_keys=[inside_rep_id]
    )
