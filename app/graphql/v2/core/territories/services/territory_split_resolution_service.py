from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from commons.db.v6.core.customers.customer_split_rate import CustomerSplitRate
from commons.db.v6.core.territories.territory import Territory

from app.graphql.v2.core.territories.repositories.territory_lookup_repository import (
    TerritoryLookupRepository,
)
from app.graphql.v2.core.territories.repositories.territory_repository import (
    TerritoryRepository,
)
from app.graphql.v2.core.territories.repositories.territory_split_rate_repository import (
    TerritorySplitRateRepository,
)


@dataclass
class ResolvedSplitRate:
    user_id: UUID
    split_rate: Decimal
    position: int
    source: str
    source_id: UUID


class TerritorySplitResolutionService:
    def __init__(
        self,
        territory_repository: TerritoryRepository,
        territory_lookup_repository: TerritoryLookupRepository,
        territory_split_rate_repository: TerritorySplitRateRepository,
    ) -> None:
        super().__init__()
        self.territory_repository = territory_repository
        self.territory_lookup_repository = territory_lookup_repository
        self.split_rate_repository = territory_split_rate_repository

    async def resolve_splits_for_customer(
        self,
        customer_splits: list[CustomerSplitRate],
        territory_id: UUID | None,
    ) -> list[ResolvedSplitRate]:
        if customer_splits:
            return [
                ResolvedSplitRate(
                    user_id=split.user_id,
                    split_rate=split.split_rate,
                    position=split.position,
                    source="customer",
                    source_id=split.customer_id,
                )
                for split in customer_splits
            ]

        if territory_id:
            return await self._get_territory_splits_with_cascade(territory_id)

        return []

    async def _get_territory_splits_with_cascade(
        self, territory_id: UUID
    ) -> list[ResolvedSplitRate]:
        hierarchy = await self.territory_repository.get_hierarchy(territory_id)

        for territory in hierarchy:
            splits = await self.split_rate_repository.get_by_territory(territory.id)
            if splits:
                return [
                    ResolvedSplitRate(
                        user_id=split.user_id,
                        split_rate=split.split_rate,
                        position=split.position,
                        source="territory",
                        source_id=territory.id,
                    )
                    for split in splits
                ]

        return []

    async def find_territory_for_address(
        self,
        zip_code: str | None = None,
        city_name: str | None = None,
        county_code: str | None = None,
        state_code: str | None = None,
    ) -> Territory | None:
        return await self.territory_lookup_repository.find_by_geographic_data(
            zip_code=zip_code,
            city_name=city_name,
            county_code=county_code,
            state_code=state_code,
        )
