
from typing import TYPE_CHECKING

from uuid import UUID

from sqlalchemy import ForeignKey, JSON, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel

if TYPE_CHECKING:
    from app.graphql.pdf_templates.models.pdf_template_model import PdfTemplate


class PdfTemplateModule(CrmBaseModel):

    __tablename__ = "pdf_template_modules"

    template_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pycrm.pdf_templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    module_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    ) 
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    config: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )

    template: Mapped["PdfTemplate"] = relationship(
        init=False, back_populates="modules", lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<PdfTemplateModule(id={self.id}, type='{self.module_type}', position={self.position})>"

