import uuid

from commons.db.v6.base import HasCreatedAt
from commons.db.v6.user.user import HasCreatedBy, User
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base_models import PyConnectPosBaseModel


class Agreement(PyConnectPosBaseModel, HasCreatedBy, HasCreatedAt, kw_only=True):
    __tablename__ = "agreements"
    __table_args__ = (
        UniqueConstraint("connected_org_id", name="uq_agreements_connected_org_id"),
        {"schema": "connect_pos", "extend_existing": True},
    )

    connected_org_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True))
    s3_key: Mapped[str] = mapped_column(String(500))
    file_name: Mapped[str] = mapped_column(String(255))
    file_size: Mapped[int]
    file_sha: Mapped[str] = mapped_column(String(64))

    created_by: Mapped[User] = relationship(init=False)
