import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.connections.exceptions import (
    UserNotFoundError,
    UserOrganizationRequiredError,
)
from app.graphql.organizations.models import RemoteUser


class UserOrgRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_org_id(self, workos_user_id: str) -> uuid.UUID:
        stmt = select(RemoteUser).where(RemoteUser.workos_user_id == workos_user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise UserNotFoundError(workos_user_id)

        if user.org_primary_id is None:
            raise UserOrganizationRequiredError(workos_user_id)

        return user.org_primary_id
