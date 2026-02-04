from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.common.services.overage_service import OverageService
from app.graphql.common.strawberry.overage_record import OverageRecord
from app.graphql.inject import inject


@strawberry.type
class OverageQueries:
    """Queries for overage calculations"""

    @strawberry.field(
        name="findEffectiveCommissionRateAndOverageUnitPriceByProduct",
        description="Calculate effective commission rate and overage unit price for a product",
    )
    @inject
    async def find_effective_commission_rate_and_overage_unit_price_by_product(
        self,
        product_id: strawberry.ID,
        detail_unit_price: float,
        factory_id: strawberry.ID,
        end_user_id: strawberry.ID,
        service: Injected[OverageService],
        quantity: float = 1.0,
    ) -> OverageRecord:
        """
        Find effective commission rate and overage unit price for a product.

        Args:
            product_id: The product UUID
            detail_unit_price: The unit price from the quote/order detail
            factory_id: The factory/manufacturer UUID
            end_user_id: The end user customer UUID
            quantity: The quantity being purchased (for quantity-based pricing)

        Returns:
            OverageRecord with calculated commission and overage values
        """
        return await service.find_effective_commission_rate_and_overage(
            product_id=UUID(product_id),
            detail_unit_price=detail_unit_price,
            factory_id=UUID(factory_id),
            end_user_id=UUID(end_user_id),
            quantity=quantity,
        )
