"""SQLAlchemy ORM model for Status entity."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasPrimaryKey

if TYPE_CHECKING:
    from app.graphql.jobs.models.jobs_model import Job


class JobStatus(CrmBaseModel, HasPrimaryKey, kw_only=True):
    __tablename__ = "job_statuses"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    jobs: Mapped[list["Job"]] = relationship(
        init=False, back_populates="status", lazy="noload"
    )

    def __repr__(self) -> str:
        """String representation of the Status."""
        return f"<Status(id={self.id}, name='{self.name}')>"
