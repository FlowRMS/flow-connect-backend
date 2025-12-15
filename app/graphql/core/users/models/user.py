import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import HasCreatedAt, LocalBaseModel


class UserV2(LocalBaseModel, HasCreatedAt):
    __tablename__ = "users"

    username: Mapped[str]
    auth_provider_id: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str]
    role_id: Mapped[uuid.UUID]
    enabled: Mapped[bool] = mapped_column(default=True)
    inside: Mapped[bool | None] = mapped_column(default=None)
    outside: Mapped[bool | None] = mapped_column(default=None)
    supervisor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, default=None
    )

    supervisor: Mapped["UserV2 | None"] = relationship(
        lazy="joined", init=False, remote_side="UserV2.id"
    )

    @hybrid_property
    def full_name(self) -> str:
        return self.first_name + " " + self.last_name
