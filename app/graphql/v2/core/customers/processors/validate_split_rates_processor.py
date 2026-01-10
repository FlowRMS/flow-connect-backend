from collections.abc import Sequence
from uuid import UUID

from commons.db.v6 import Customer, CustomerSplitRate, RepTypeEnum, User
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
    InvalidInsideRepError,
    InvalidOutsideRepError,
    UserNotFoundInSplitRateError,
)


class ValidateSplitRatesProcessor(BaseProcessor[Customer]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[Customer]) -> None:
        customer = context.entity
        split_rates: list[
            CustomerSplitRate
        ] = await customer.awaitable_attrs.split_rates
        if not split_rates:
            return

        user_ids = [rate.user_id for rate in split_rates]
        self._validate_unique_user_ids(user_ids)
        users = await self._get_users_by_ids(user_ids)
        user_map = {user.id: user for user in users}

        inside_rates: list[CustomerSplitRate] = []
        outside_rates: list[CustomerSplitRate] = []

        for rate in split_rates:
            user = user_map.get(rate.user_id)
            if not user:
                raise UserNotFoundInSplitRateError(rate.user_id)

            self._validate_rep_type(user, rate.rep_type)

            if rate.rep_type == RepTypeEnum.INSIDE:
                inside_rates.append(rate)
            else:
                outside_rates.append(rate)

        validate_split_rates_sum_to_100(inside_rates, label="inside split rates")
        validate_split_rates_sum_to_100(outside_rates, label="outside split rates")

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

    def _validate_rep_type(self, user: User, rep_type: RepTypeEnum) -> None:
        if rep_type == RepTypeEnum.INSIDE and not user.inside:
            raise InvalidInsideRepError(user.first_name, user.last_name)

        if rep_type == RepTypeEnum.OUTSIDE and not user.outside:
            raise InvalidOutsideRepError(user.first_name, user.last_name)
