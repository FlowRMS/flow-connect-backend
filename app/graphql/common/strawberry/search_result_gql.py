import uuid
from collections.abc import Sequence
from typing import Self

import strawberry
from sqlalchemy.engine.row import Row

from app.graphql.common.strawberry.source_type import SourceType


@strawberry.type(name="SearchResult")
class SearchResultGQL:
    id: uuid.UUID
    title: str
    alias: str | None
    result_type: SourceType
    extra_info: str | None

    @classmethod
    def from_row(
        cls, row: Row[tuple[uuid.UUID, str, str | None, float, int, str | None]]
    ) -> Self:
        return cls(
            id=row[0],
            title=row[1],
            alias=row[2],
            result_type=SourceType(int(row[4])),
            extra_info=row[5] if len(row) > 5 else None,
        )

    @classmethod
    def from_row_list(
        cls,
        rows: Sequence[Row[tuple[uuid.UUID, str, str | None, float, int, str | None]]],
    ) -> list[Self]:
        return [cls.from_row(row) for row in rows]
