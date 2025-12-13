from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import HasCreatedAt, HasCreatedBy, LocalBaseModel

if TYPE_CHECKING:
    from .product import ProductV2


class ProductUomV2(LocalBaseModel, HasCreatedBy, HasCreatedAt):
    __tablename__ = "product_uoms"

    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(default=None)
    multiply: Mapped[bool] = mapped_column(default=False)
    multiply_by: Mapped[int] = mapped_column(default=1)
    products: Mapped[list["ProductV2"]] = relationship(
        lazy="noload", init=False, back_populates="uom"
    )
