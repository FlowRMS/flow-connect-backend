import uuid
from datetime import datetime

from commons.db.v6.base import HasCreatedAt, PyCRMBaseModel
from commons.db.v6.crm.jobs.jobs_model import Job
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class JobEmbedding(PyCRMBaseModel, HasCreatedAt, kw_only=True):
    __tablename__ = "job_embeddings"

    job_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pycrm.jobs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    embedding_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    text_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    job: Mapped[Job] = relationship(
        init=False,
        lazy="joined",
    )
