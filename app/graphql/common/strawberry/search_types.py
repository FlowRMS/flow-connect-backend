import enum
import uuid
from collections.abc import Sequence
from enum import auto
from typing import Self

import strawberry
from sqlalchemy.engine.row import Row


@strawberry.enum
class SourceType(enum.IntEnum):
    CONTACT = auto()
    COMPANY = auto()
    JOB = auto()
    TASK = auto()
    NOTE = auto()
    CAMPAIGN = auto()
    QUOTE = auto()
    PRE_OPPORTUNITY = auto()
    SPEC_SHEET = auto()
    CUSTOMER = auto()
    FACTORY = auto()
    PRODUCT = auto()
    INVOICE = auto()
    ORDER = auto()
    CREDIT = auto()
    CHECK = auto()
    ADJUSTMENT = auto()
    ADDRESS = auto()
    SHIPPING_CARRIER = auto()
    CONTAINER_TYPE = auto()
    WAREHOUSE = auto()
    ORDER_ACKNOWLEDGEMENT = auto()
    FOLDER = auto()


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
