from collections.abc import Sequence
from typing import Any

from sqlalchemy import Result, Row
from sqlalchemy.ext.asyncio import AsyncSession


class UniversalSearchRepository:
    def __init__(self, session: AsyncSession) -> None:  # pyright: ignore[reportMissingSuperCall]
        self.session = session

    async def execute_search_query(self, combined_query: Any) -> Sequence[Row[Any]]:
        result: Result[Any] = await self.session.execute(combined_query)
        return result.fetchall()
