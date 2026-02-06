from typing import Any

import strawberry
from strawberry.scalars import JSON

from app.graphql.pos.validations.constants import get_issue_title


@strawberry.type
class FileValidationIssueLiteResponse:
    id: strawberry.ID
    row_number: int
    title: str
    column_name: str | None
    file_id: strawberry.ID
    file_name: str

    @staticmethod
    def from_model(issue: Any) -> "FileValidationIssueLiteResponse":
        return FileValidationIssueLiteResponse(
            id=strawberry.ID(str(issue.id)),
            row_number=issue.row_number,
            title=get_issue_title(issue.validation_key, issue.column_name),
            column_name=issue.column_name,
            file_id=strawberry.ID(str(issue.exchange_file.id)),
            file_name=issue.exchange_file.file_name,
        )


@strawberry.type
class FileValidationIssueResponse:
    id: strawberry.ID
    row_number: int
    title: str
    column_name: str | None
    validation_key: str
    message: str
    file_id: strawberry.ID
    file_name: str
    row_data: JSON | None

    @staticmethod
    def from_model(issue: Any) -> "FileValidationIssueResponse":
        return FileValidationIssueResponse(
            id=strawberry.ID(str(issue.id)),
            row_number=issue.row_number,
            title=get_issue_title(issue.validation_key, issue.column_name),
            column_name=issue.column_name,
            validation_key=issue.validation_key,
            message=issue.message,
            file_id=strawberry.ID(str(issue.exchange_file.id)),
            file_name=issue.exchange_file.file_name,
            row_data=issue.row_data,
        )


@strawberry.type
class ValidationKeyGroupResponse:
    validation_key: str
    title: str
    items: list[FileValidationIssueLiteResponse]
    count: int


@strawberry.type
class FileGroupResponse:
    file_id: strawberry.ID
    file_name: str
    items: list[FileValidationIssueLiteResponse]
    count: int
    groups: list[ValidationKeyGroupResponse]


@strawberry.type
class ValidationIssueGroupResponse:
    items: list[FileValidationIssueLiteResponse]
    count: int
    files: list[FileGroupResponse]


@strawberry.type
class FileValidationIssuesResponse:
    blocking: ValidationIssueGroupResponse
    warning: ValidationIssueGroupResponse
    fyi: ValidationIssueGroupResponse
