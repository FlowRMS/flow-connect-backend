from collections.abc import Sequence
from uuid import UUID

from commons.db.v6 import User
from commons.db.v6.core.factories.factory import Factory
from commons.db.v6.core.factories.factory_split_rate import FactorySplitRate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors import (
    BaseProcessor,
    EntityContext,
    RepositoryEvent,
    validate_split_rates_sum_to_100,
)
from app.errors.split_rate_errors import (
    DuplicateUserInSplitRatesError,
    InvalidFactoryRepError,
    UserNotFoundInSplitRateError,
)


class ValidateFactorySplitRatesProcessor(BaseProcessor[Factory]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[Factory]) -> None:
        factory = context.entity
        split_rates: list[FactorySplitRate] = await factory.awaitable_attrs.split_rates
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

            if not user.inside:
                raise InvalidFactoryRepError(user.first_name, user.last_name)

        validate_split_rates_sum_to_100(split_rates, label="factory split rates")

    async def _get_users_by_ids(self, user_ids: list[UUID]) -> Sequence[User]:
        stmt = select(User).where(User.id.in_(user_ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    def _validate_unique_user_ids(self, user_ids: list[UUID]) -> None:
        seen: set[UUID] = set()
        duplicates: set[UUID] = set()
        for user_id in user_ids:
            if user_id in seen:
                duplicates.add(user_id)
            seen.add(user_id)
        if duplicates:
            raise DuplicateUserInSplitRatesError(duplicates)
