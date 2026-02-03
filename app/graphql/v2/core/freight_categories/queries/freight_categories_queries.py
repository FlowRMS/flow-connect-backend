from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.freight_categories.services.freight_category_service import (
    FreightCategoryService,
)
from app.graphql.v2.core.freight_categories.strawberry.freight_category_response import (
    FreightCategoryResponse,
)


@strawberry.type
class FreightCategoriesQueries:
    @strawberry.field
    @inject
    async def freight_categories(
        self,
        service: Injected[FreightCategoryService],
    ) -> list[FreightCategoryResponse]:
        """Get all freight categories ordered by display order."""
        freight_categories = await service.list_all()
        return FreightCategoryResponse.from_orm_model_list(freight_categories)

    @strawberry.field
    @inject
    async def active_freight_categories(
        self,
        service: Injected[FreightCategoryService],
    ) -> list[FreightCategoryResponse]:
        """Get active freight categories ordered by display order (for dropdowns)."""
        freight_categories = await service.list_active()
        return FreightCategoryResponse.from_orm_model_list(freight_categories)

    @strawberry.field
    @inject
    async def freight_category(
        self,
        id: UUID,
        service: Injected[FreightCategoryService],
    ) -> FreightCategoryResponse:
        """Get a freight category by ID."""
        freight_category = await service.get_by_id(id)
        return FreightCategoryResponse.from_orm_model(freight_category)
