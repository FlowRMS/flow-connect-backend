from typing import Any, Self
from uuid import UUID

import strawberry
from commons.db.v6.enums import DocumentEntityType
from commons.db.v6.files import FileType
from sqlalchemy.engine.row import Row

from app.core.db.adapters.dto import LandingPageInterfaceBase


@strawberry.type(name="FileLandingPage")
class FileLandingPageResponse(LandingPageInterfaceBase):
    file_name: str
    file_path: str
    file_size: int
    file_entity_type: DocumentEntityType | None
    file_type: str | None
    file_sha: str | None
    archived: bool
    folder_id: UUID | None

    @classmethod
    def from_orm_model(cls, row: Row[Any]) -> Self:
        data = cls.unpack_row(row)
        file_type_value = data.pop("file_type", None)
        if file_type_value is not None:
            data["file_type"] = FileType(file_type_value).name
        else:
            data["file_type"] = None
        return cls(**data)
