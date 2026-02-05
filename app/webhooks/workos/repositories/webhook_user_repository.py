from commons.db.v6.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class WebhookUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush([user])
        return user

    async def update(self, user: User) -> None:
        await self.session.flush([user])
