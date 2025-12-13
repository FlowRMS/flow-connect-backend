import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import HasCreatedAt, HasCreatedBy, LocalBaseModel
from app.graphql.core.factories.models.factory import FactoryV2

from .product_category import ProductCategoryV2
from .product_uom import ProductUomV2


class ProductV2(LocalBaseModel, HasCreatedBy, HasCreatedAt):
    __tablename__ = "products"

    factory_part_number: Mapped[str]
    factory_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(FactoryV2.id))
    unit_price: Mapped[Decimal]
    default_commission_rate: Mapped[Decimal]
    product_category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(ProductCategoryV2.id)
    )
    product_uom_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(ProductUomV2.id)
    )
    published: Mapped[bool] = mapped_column(default=False)
    approval_needed: Mapped[bool | None] = mapped_column(default=False)
    description: Mapped[str | None] = mapped_column(default=None)
    lead_time: Mapped[str | None] = mapped_column(default=None)
    min_order_qty: Mapped[int | None] = mapped_column(default=None)
    commission_discount_rate: Mapped[Decimal | None] = mapped_column(default=None)
    overall_discount_rate: Mapped[Decimal | None] = mapped_column(default=None)
    cost: Mapped[Decimal | None] = mapped_column(default=None)
    individual_upc: Mapped[str | None] = mapped_column(default=None)
    approval_comments: Mapped[str | None] = mapped_column(default=None)
    logo_url: Mapped[str | None] = mapped_column(default=None)
    sales_model: Mapped[str | None] = mapped_column(default=None)
    payout_type: Mapped[str | None] = mapped_column(default=None)

    category: Mapped[ProductCategoryV2] = relationship(lazy="joined", init=False)
    factory: Mapped[FactoryV2] = relationship(lazy="joined", init=False)
    uom: Mapped[ProductUomV2 | None] = relationship(
        lazy="joined", init=False, back_populates="products"
    )
