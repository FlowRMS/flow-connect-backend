from decimal import Decimal
from uuid import UUID

from commons.db.v6 import User
from commons.db.v6.core.territories.territory import Territory
from commons.db.v6.core.territories.territory_split_rate import TerritorySplitRate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent
from app.errors.common_errors import ValidationError
from app.errors.split_rate_errors import (
    DuplicateUserInSplitRatesError,
    InvalidOutsideRepError,
    UserNotFoundInSplitRateError,
)


class ValidateTerritorySplitRatesProcessor(BaseProcessor[Territory]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session
        self._user_cache: dict[UUID, User] = {}

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[Territory]) -> None:
        territory = context.entity
        split_rates: list[
            TerritorySplitRate
        ] = await territory.awaitable_attrs.split_rates

        if not split_rates:
            return

        user_ids = [rate.user_id for rate in split_rates]
        self._validate_unique_user_ids(user_ids)
        users = await self._get_users_by_ids(user_ids)
        user_map = {user.id: user for user in users}

        for rate in split_rates:
            user = user_map.get(rate.user_id)
            if not user:
                raise UserNotFoundInSplitRateError(rate.user_id)

            if not user.outside:
                raise InvalidOutsideRepError(user.first_name, user.last_name)

        self._validate_split_rates_sum(split_rates)

    async def _get_users_by_ids(self, user_ids: list[UUID]) -> list[User]:
        missing_ids = [uid for uid in user_ids if uid not in self._user_cache]
        if missing_ids:
            stmt = select(User).where(User.id.in_(missing_ids))
            result = await self.session.execute(stmt)
            for user in result.scalars().all():
                self._user_cache[user.id] = user
        return [self._user_cache[uid] for uid in user_ids if uid in self._user_cache]

    def _validate_unique_user_ids(self, user_ids: list[UUID]) -> None:
        seen: set[UUID] = set()
        duplicates: set[UUID] = set()
        for user_id in user_ids:
            if user_id in seen:
                duplicates.add(user_id)
            seen.add(user_id)
        if duplicates:
            raise DuplicateUserInSplitRatesError(duplicates)

    def _validate_split_rates_sum(self, rates: list[TerritorySplitRate]) -> None:
        if not rates:
            return
        total = sum(rate.split_rate for rate in rates)
        total = Decimal(total).quantize(Decimal("0.01"))
        if total != Decimal("100"):
            raise ValidationError(
                f"Total territory split rates must equal 100%. Got: {total}%"
            )
