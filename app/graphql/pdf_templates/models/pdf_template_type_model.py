

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasCreatedAt, HasCreatedBy

if TYPE_CHECKING:
    from app.graphql.pdf_templates.models.pdf_template_model import PdfTemplate


class PdfTemplateType(CrmBaseModel, HasCreatedAt, HasCreatedBy, kw_only=True):

    __tablename__ = "pdf_template_types"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    display_order: Mapped[int | None] = mapped_column(nullable=True)

    templates: Mapped[list["PdfTemplate"]] = relationship(
        init=False,
        back_populates="template_type",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<PdfTemplateType(id={self.id}, name='{self.name}')>"

