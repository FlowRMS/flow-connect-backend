from commons.db.v6.core.products.product_uom import ProductUom
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class ProductUomRepository(BaseRepository[ProductUom]):
    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, ProductUom)
