from collections.abc import Sequence
from uuid import UUID

from commons.db.v6 import Customer, RepTypeEnum, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.processors import (
    BaseProcessor,
    EntityContext,
    RepositoryEvent,
)
from app.errors.common_errors import ValidationError


class ValidateSplitRatesProcessor(BaseProcessor[Customer]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[Customer]) -> None:
        customer = context.entity
        if not customer.split_rates:
            return

        user_ids = [rate.user_id for rate in customer.split_rates]
        users = await self._get_users_by_ids(user_ids)
        user_map = {user.id: user for user in users}

        for rate in customer.split_rates:
            user = user_map.get(rate.user_id)
            if not user:
                raise ValidationError(f"User with ID '{rate.user_id}' not found")

            self._validate_rep_type(user, rate.rep_type)

    async def _get_users_by_ids(self, user_ids: list[UUID]) -> Sequence[User]:
        stmt = select(User).where(User.id.in_(user_ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    def _validate_rep_type(self, user: User, rep_type: RepTypeEnum) -> None:
        if rep_type == RepTypeEnum.INSIDE and not user.inside:
            raise ValidationError(
                f"User '{user.first_name} {user.last_name}' cannot be an inside rep "
                "(inside flag is not set)"
            )

        if rep_type == RepTypeEnum.OUTSIDE and not user.outside:
            raise ValidationError(
                f"User '{user.first_name} {user.last_name}' cannot be an outside rep "
                "(outside flag is not set)"
            )
