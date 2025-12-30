import uuid

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.products.services.product_category_service import (
    ProductCategoryService,
)
from app.graphql.v2.core.products.strawberry.product_category_response import (
    ProductCategoryResponse,
)


@strawberry.type
class ProductCategoryQueries:
    @strawberry.field
    @inject
    async def product_categories(
        self,
        service: Injected[ProductCategoryService],
        factory_id: strawberry.Maybe[uuid.UUID] = None,
        parent_id: strawberry.Maybe[uuid.UUID] = None,
        grandparent_id: strawberry.Maybe[uuid.UUID] = None,
    ) -> list[ProductCategoryResponse]:
        factory_id_value = factory_id.value if factory_id else None
        parent_id_value = parent_id.value if parent_id else None
        grandparent_id_value = grandparent_id.value if grandparent_id else None
        return ProductCategoryResponse.from_orm_model_list(
            await service.list_with_filters(
                factory_id=factory_id_value,
                parent_id=parent_id_value,
                grandparent_id=grandparent_id_value,
            )
        )
