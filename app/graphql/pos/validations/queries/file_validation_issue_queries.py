import uuid

import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.pos.validations.constants import get_issue_title
from app.graphql.pos.validations.models import FileValidationIssue
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_validation_issue_service import (
    FileValidationIssueService,
)
from app.graphql.pos.validations.strawberry.file_validation_issue_types import (
    FileGroupResponse,
    FileValidationIssueLiteResponse,
    FileValidationIssueResponse,
    FileValidationIssuesResponse,
    ValidationIssueGroupResponse,
    ValidationKeyGroupResponse,
)


def _build_group(
    files_by_key: dict[uuid.UUID, dict[str, list[FileValidationIssue]]],
) -> ValidationIssueGroupResponse:
    all_issues = [
        issue
        for keys in files_by_key.values()
        for issues in keys.values()
        for issue in issues
    ]
    files = [_build_file_group(file_id, keys) for file_id, keys in files_by_key.items()]
    return ValidationIssueGroupResponse(
        items=[
            FileValidationIssueLiteResponse.from_model(issue) for issue in all_issues
        ],
        count=len(all_issues),
        files=files,
    )


def _build_file_group(
    file_id: uuid.UUID,
    issues_by_key: dict[str, list[FileValidationIssue]],
) -> FileGroupResponse:
    all_issues = [issue for issues in issues_by_key.values() for issue in issues]
    file_name = all_issues[0].exchange_file.file_name if all_issues else ""
    groups = [
        ValidationKeyGroupResponse(
            validation_key=key,
            title=get_issue_title(key, None),
            items=[
                FileValidationIssueLiteResponse.from_model(issue) for issue in issues
            ],
            count=len(issues),
        )
        for key, issues in issues_by_key.items()
    ]
    return FileGroupResponse(
        file_id=strawberry.ID(str(file_id)),
        file_name=file_name,
        items=[
            FileValidationIssueLiteResponse.from_model(issue) for issue in all_issues
        ],
        count=len(all_issues),
        groups=groups,
    )


@strawberry.type
class FileValidationIssueQueries:
    @strawberry.field()
    @inject
    async def file_validation_issues(
        self,
        service: Injected[FileValidationIssueService],
    ) -> FileValidationIssuesResponse:
        grouped = await service.get_pending_issues_grouped()

        return FileValidationIssuesResponse(
            blocking=_build_group(grouped[ValidationType.STANDARD_VALIDATION]),
            warning=_build_group(grouped[ValidationType.VALIDATION_WARNING]),
            fyi=_build_group(grouped[ValidationType.AI_POWERED_VALIDATION]),
        )

    @strawberry.field()
    @inject
    async def file_validation_issue(
        self,
        id: strawberry.ID,
        service: Injected[FileValidationIssueService],
    ) -> FileValidationIssueResponse | None:
        issue = await service.get_by_id(uuid.UUID(str(id)))
        if issue is None:
            return None
        return FileValidationIssueResponse.from_model(issue)

    @strawberry.field()
    @inject
    async def filtered_file_validation_issues(
        self,
        validation_type: ValidationType,
        file_id: strawberry.ID,
        validation_key: str,
        service: Injected[FileValidationIssueService],
    ) -> list[FileValidationIssueResponse]:
        issues = await service.get_filtered_issues(
            validation_type, uuid.UUID(str(file_id)), validation_key
        )
        return [FileValidationIssueResponse.from_model(issue) for issue in issues]
