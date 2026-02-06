import uuid

from app.graphql.pos.data_exchange.models import ValidationStatus
from app.graphql.pos.data_exchange.repositories import ExchangeFileRepository
from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.field_map.models.field_map_enums import (
    FieldMapDirection,
    FieldMapType,
)
from app.graphql.pos.field_map.repositories.field_map_repository import (
    FieldMapRepository,
)
from app.graphql.pos.validations.constants import BLOCKING_VALIDATION_KEYS
from app.graphql.pos.validations.exceptions import FieldMapNotFoundError
from app.graphql.pos.validations.models import FileValidationIssue
from app.graphql.pos.validations.repositories import FileValidationIssueRepository
from app.graphql.pos.validations.services.file_reader_service import (
    FileReaderService,
    FileRow,
)
from app.graphql.pos.validations.services.validation_pipeline import ValidationPipeline
from app.graphql.pos.validations.services.validators.base import ValidationIssue
from app.graphql.pos.validations.services.validators.date_format_validator import (
    DateFormatValidator,
)
from app.graphql.pos.validations.services.validators.future_date_validator import (
    FutureDateValidator,
)
from app.graphql.pos.validations.services.validators.lost_flag_validator import (
    LostFlagValidator,
)
from app.graphql.pos.validations.services.validators.lot_order_detection_validator import (
    LotOrderDetectionValidator,
)
from app.graphql.pos.validations.services.validators.numeric_field_validator import (
    NumericFieldValidator,
)
from app.graphql.pos.validations.services.validators.price_calculation_validator import (
    PriceCalculationValidator,
)
from app.graphql.pos.validations.services.validators.required_field_validator import (
    RequiredFieldValidator,
)
from app.graphql.pos.validations.services.validators.ship_from_location_validator import (
    ShipFromLocationValidator,
)
from app.graphql.pos.validations.services.validators.zip_code_validator import (
    ZipCodeValidator,
)


class ValidationExecutionService:
    def __init__(
        self,
        exchange_file_repository: ExchangeFileRepository,
        file_reader_service: FileReaderService,
        validation_issue_repository: FileValidationIssueRepository,
        field_map_repository: FieldMapRepository,
    ) -> None:
        self.exchange_file_repository = exchange_file_repository
        self.file_reader_service = file_reader_service
        self.validation_issue_repository = validation_issue_repository
        self.field_map_repository = field_map_repository

    async def validate_file(self, file_id: uuid.UUID) -> None:
        file = await self.exchange_file_repository.get_by_id(file_id)
        if file is None:
            return

        file.validation_status = ValidationStatus.VALIDATING.value
        await self.exchange_file_repository.update(file)

        await self.validation_issue_repository.delete_by_file_id(file_id)

        field_maps = await self._get_applicable_field_maps(
            file.org_id, file.is_pos, file.is_pot
        )
        if not field_maps:
            raise FieldMapNotFoundError(
                f"No field map found for organization {file.org_id}"
            )

        all_issues: list[ValidationIssue] = []
        has_blocking_errors = False

        for field_map in field_maps:
            rows = await self.file_reader_service.read_file(
                s3_key=file.s3_key,
                file_type=file.file_type,
                field_map=field_map,
            )

            issues, has_blocking = self._run_validation(rows, field_map)
            all_issues.extend(issues)
            if has_blocking:
                has_blocking_errors = True

        if all_issues:
            issue_models = [
                FileValidationIssue(
                    exchange_file_id=file_id,
                    row_number=issue.row_number,
                    column_name=issue.column_name,
                    validation_key=issue.validation_key,
                    message=issue.message,
                    row_data=issue.row_data,
                )
                for issue in all_issues
            ]
            await self.validation_issue_repository.create_bulk(issue_models)

        file.validation_status = (
            ValidationStatus.INVALID.value
            if has_blocking_errors
            else ValidationStatus.VALID.value
        )
        await self.exchange_file_repository.update(file)

    async def _get_applicable_field_maps(
        self,
        org_id: uuid.UUID,
        is_pos: bool,
        is_pot: bool,
    ) -> list[FieldMap]:
        field_maps: list[FieldMap] = []

        if is_pos:
            pos_map = await self.field_map_repository.get_by_org_and_type(
                org_id, FieldMapType.POS, FieldMapDirection.SEND
            )
            if pos_map:
                field_maps.append(pos_map)

        if is_pot:
            pot_map = await self.field_map_repository.get_by_org_and_type(
                org_id, FieldMapType.POT, FieldMapDirection.SEND
            )
            if pot_map:
                field_maps.append(pot_map)

        return field_maps

    def _run_validation(
        self,
        rows: list[FileRow],
        field_map: FieldMap,
    ) -> tuple[list[ValidationIssue], bool]:
        pipeline = self._create_pipeline()
        all_issues = pipeline.validate_rows(rows, field_map)

        has_blocking = any(
            issue.validation_key in BLOCKING_VALIDATION_KEYS for issue in all_issues
        )

        return all_issues, has_blocking

    @staticmethod
    def _create_pipeline() -> ValidationPipeline:
        return ValidationPipeline(
            blocking_validators=[
                RequiredFieldValidator(),
                DateFormatValidator(),
                NumericFieldValidator(),
                ZipCodeValidator(),
                PriceCalculationValidator(),
                FutureDateValidator(),
            ],
            warning_validators=[
                LotOrderDetectionValidator(),
                ShipFromLocationValidator(),
                LostFlagValidator(),
            ],
        )
