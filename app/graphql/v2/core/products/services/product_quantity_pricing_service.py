from uuid import UUID

from commons.db.v6.core.products.product_quantity_pricing import ProductQuantityPricing

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.products.repositories.product_quantity_pricing_repository import (
    ProductQuantityPricingRepository,
)
from app.graphql.v2.core.products.strawberry.product_quantity_pricing_input import (
    ProductQuantityPricingInput,
)


class ProductQuantityPricingService:
    def __init__(self, repository: ProductQuantityPricingRepository) -> None:
        super().__init__()
        self.repository = repository

    async def get_by_id(self, pricing_id: UUID) -> ProductQuantityPricing:
        pricing = await self.repository.get_by_id(pricing_id)
        if not pricing:
            raise NotFoundError(
                f"ProductQuantityPricing with id {pricing_id} not found"
            )
        return pricing

    async def list_by_product_id(
        self, product_id: UUID
    ) -> list[ProductQuantityPricing]:
        return await self.repository.list_by_product_id(product_id)

    async def create(
        self, pricing_input: ProductQuantityPricingInput
    ) -> ProductQuantityPricing:
        pricing = await self.repository.create(pricing_input.to_orm_model())
        return await self.get_by_id(pricing.id)

    async def update(
        self, pricing_id: UUID, pricing_input: ProductQuantityPricingInput
    ) -> ProductQuantityPricing:
        pricing = pricing_input.to_orm_model()
        pricing.id = pricing_id
        _ = await self.repository.update(pricing)
        return await self.get_by_id(pricing_id)

    async def delete(self, pricing_id: UUID) -> bool:
        if not await self.repository.exists(pricing_id):
            raise NotFoundError(
                f"ProductQuantityPricing with id {pricing_id} not found"
            )
        return await self.repository.delete(pricing_id)
