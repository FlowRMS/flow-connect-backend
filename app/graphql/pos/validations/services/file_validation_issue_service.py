import uuid
from collections import defaultdict

from app.graphql.pos.validations.constants import BLOCKING_VALIDATION_KEYS
from app.graphql.pos.validations.models import FileValidationIssue
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.repositories import FileValidationIssueRepository

GroupedByFileAndKey = dict[
    ValidationType, dict[uuid.UUID, dict[str, list[FileValidationIssue]]]
]


class FileValidationIssueService:
    def __init__(self, repository: FileValidationIssueRepository) -> None:
        self.repository = repository

    async def get_pending_issues_grouped(self) -> GroupedByFileAndKey:
        issues = await self.repository.get_by_pending_files()

        grouped: GroupedByFileAndKey = {
            ValidationType.STANDARD_VALIDATION: {},
            ValidationType.VALIDATION_WARNING: {},
            ValidationType.AI_POWERED_VALIDATION: {},
        }

        for issue in issues:
            validation_type = self._get_validation_type(issue.validation_key)
            file_id = issue.exchange_file_id
            by_file = grouped[validation_type]
            if file_id not in by_file:
                by_file[file_id] = defaultdict(list)
            by_file[file_id][issue.validation_key].append(issue)

        return grouped

    async def get_by_id(self, issue_id: uuid.UUID) -> FileValidationIssue | None:
        return await self.repository.get_by_id(issue_id)

    async def get_filtered_issues(
        self,
        validation_type: ValidationType,
        file_id: uuid.UUID,
        validation_key: str,
    ) -> list[FileValidationIssue]:
        actual_type = self._get_validation_type(validation_key)
        if actual_type != validation_type:
            return []
        return await self.repository.get_by_file_and_key(file_id, validation_key)

    @staticmethod
    def _get_validation_type(validation_key: str) -> ValidationType:
        if validation_key in BLOCKING_VALIDATION_KEYS:
            return ValidationType.STANDARD_VALIDATION
        return ValidationType.VALIDATION_WARNING
