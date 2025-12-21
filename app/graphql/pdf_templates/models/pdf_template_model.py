
from typing import TYPE_CHECKING
from uuid import UUID

from commons.db.models import User
from sqlalchemy import Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasCreatedAt, HasCreatedBy, HasUpdatedAt

if TYPE_CHECKING:
    from app.graphql.pdf_templates.models.pdf_template_module_model import PdfTemplateModule
    from app.graphql.pdf_templates.models.pdf_template_type_model import PdfTemplateType


class PdfTemplate(CrmBaseModel, HasCreatedAt, HasCreatedBy, HasUpdatedAt, kw_only=True):

    __tablename__ = "pdf_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    template_type_code: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    template_type_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pycrm.pdf_template_types.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    global_styles: Mapped[dict] = mapped_column(
        JSON, nullable=False, default=dict
    )

    template_type: Mapped["PdfTemplateType | None"] = relationship(
        init=False, back_populates="templates", lazy="joined"
    )
    modules: Mapped[list["PdfTemplateModule"]] = relationship(
        init=False,
        back_populates="template",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="PdfTemplateModule.position",
    )
    created_by: Mapped[User] = relationship(init=False, lazy="joined")

    def __repr__(self) -> str:
        return f"<PdfTemplate(id={self.id}, name='{self.name}', type='{self.template_type_code}')>"

