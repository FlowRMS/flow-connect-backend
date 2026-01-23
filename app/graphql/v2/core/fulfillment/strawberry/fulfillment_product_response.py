"""Fulfillment-specific product response with factory field."""

import strawberry

from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.products.strawberry.product_response import ProductLiteResponse


@strawberry.type
class FulfillmentProductResponse(ProductLiteResponse):
    """Product response for fulfillment context - includes factory."""

    @strawberry.field
    def factory(self) -> FactoryLiteResponse | None:
        """Get factory - relationship must be eager-loaded in fulfillment queries."""
        if self._instance.factory is None:
            return None
        return FactoryLiteResponse.from_orm_model(self._instance.factory)
