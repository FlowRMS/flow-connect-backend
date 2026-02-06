from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_reader_service import FileRow


@dataclass
class ValidationIssue:
    row_number: int
    column_name: str | None
    validation_key: str
    message: str
    row_data: dict[str, Any] | None = field(default=None)


class BaseValidator(ABC):
    validation_key: str
    validation_type: ValidationType

    @abstractmethod
    def validate(self, row: FileRow, field_map: FieldMap) -> list[ValidationIssue]:
        pass
