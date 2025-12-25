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
)
from app.errors.common_errors import ValidationError


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
        users = await self._get_users_by_ids(user_ids)
        user_map = {user.id: user for user in users}

        for rate in split_rates:
            user = user_map.get(rate.user_id)
            if not user:
                raise ValidationError(f"User with ID '{rate.user_id}' not found")

            if not user.inside:
                raise ValidationError(
                    f"User '{user.first_name} {user.last_name}' cannot be a factory rep "
                    "(inside flag is not set)"
                )

    async def _get_users_by_ids(self, user_ids: list[UUID]) -> Sequence[User]:
        stmt = select(User).where(User.id.in_(user_ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()
