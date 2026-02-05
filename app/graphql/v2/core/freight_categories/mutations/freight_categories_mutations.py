from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.freight_categories.services.freight_category_service import (
    FreightCategoryService,
)
from app.graphql.v2.core.freight_categories.strawberry.freight_category_input import (
    FreightCategoryInput,
)
from app.graphql.v2.core.freight_categories.strawberry.freight_category_response import (
    FreightCategoryResponse,
)


@strawberry.type
class FreightCategoriesMutations:
    @strawberry.mutation
    @inject
    async def create_freight_category(
        self,
        input: FreightCategoryInput,
        service: Injected[FreightCategoryService],
    ) -> FreightCategoryResponse:
        freight_category = await service.create(input)
        return FreightCategoryResponse.from_orm_model(freight_category)

    @strawberry.mutation
    @inject
    async def update_freight_category(
        self,
        id: UUID,
        input: FreightCategoryInput,
        service: Injected[FreightCategoryService],
    ) -> FreightCategoryResponse:
        freight_category = await service.update(id, input)
        return FreightCategoryResponse.from_orm_model(freight_category)

    @strawberry.mutation
    @inject
    async def delete_freight_category(
        self,
        id: UUID,
        service: Injected[FreightCategoryService],
    ) -> bool:
        return await service.delete(id)

    @strawberry.mutation
    @inject
    async def reorder_freight_categories(
        self,
        ordered_ids: list[UUID],
        service: Injected[FreightCategoryService],
    ) -> list[FreightCategoryResponse]:
        """Reorder freight categories based on the provided ID list.

        The order of IDs in the list determines the new display order.
        """
        freight_categories = await service.reorder(ordered_ids)
        return FreightCategoryResponse.from_orm_model_list(freight_categories)
