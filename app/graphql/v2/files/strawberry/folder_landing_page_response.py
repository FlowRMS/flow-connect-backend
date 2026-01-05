from typing import Any, Self
from uuid import UUID

import strawberry
from sqlalchemy.engine.row import Row

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="FolderLandingPage")
class FolderLandingPageResponse(LandingPageInterfaceBase):
    name: str
    description: str | None
    parent_id: UUID | None
    archived: bool

    @classmethod
    def from_orm_model(cls, row: Row[Any]) -> Self:
        data = cls.unpack_row(row)
        return cls(**data)
