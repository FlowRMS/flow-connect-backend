import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import HasCreatedAt, HasCreatedByV2, LocalBaseModel
from app.graphql.v2.core.factories.models.factory import FactoryV2


class ProductCategoryV2(LocalBaseModel, HasCreatedByV2, HasCreatedAt):
    __tablename__ = "product_categories"

    title: Mapped[str]
    factory_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(FactoryV2.id), nullable=False
    )
    commission_rate: Mapped[Decimal]

    factory: Mapped[FactoryV2] = relationship(lazy="joined", init=False)
