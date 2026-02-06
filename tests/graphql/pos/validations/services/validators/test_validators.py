import uuid
from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from app.graphql.pos.field_map.models.field_map import FieldMap, FieldMapField
from app.graphql.pos.field_map.models.field_map_enums import (
    FieldCategory,
    FieldStatus,
    FieldType,
)
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validators.catalog_number_format_validator import (
    CatalogNumberFormatValidator,
)
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


def create_field_map_field(
    standard_field_key: str,
    field_type: FieldType = FieldType.TEXT,
    status: FieldStatus = FieldStatus.REQUIRED,
    organization_field_name: str | None = None,
) -> MagicMock:
    field = MagicMock(spec=FieldMapField)
    field.standard_field_key = standard_field_key
    field.field_type = field_type
    field.field_type_enum = field_type
    field.status = status.value
    field.status_enum = status
    field.organization_field_name = organization_field_name
    field.category = FieldCategory.TRANSACTION.value
    return field


def create_field_map(fields: list[MagicMock]) -> MagicMock:
    field_map = MagicMock(spec=FieldMap)
    field_map.id = uuid.uuid4()
    field_map.fields = fields
    return field_map


class TestRequiredFieldValidator:
    @pytest.fixture
    def validator(self) -> RequiredFieldValidator:
        return RequiredFieldValidator()

    def test_required_field_missing_returns_issue(
        self, validator: RequiredFieldValidator
    ) -> None:
        """Missing required field creates issue."""
        row = FileRow(row_number=2, data={"other_field": "value"})
        field_map = create_field_map([
            create_field_map_field("transaction_date", status=FieldStatus.REQUIRED),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 1
        assert issues[0].validation_key == "required_field"
        assert "transaction_date" in issues[0].message

    def test_required_field_present_passes(
        self, validator: RequiredFieldValidator
    ) -> None:
        """Present field passes."""
        row = FileRow(row_number=2, data={"transaction_date": "2026-01-01"})
        field_map = create_field_map([
            create_field_map_field("transaction_date", status=FieldStatus.REQUIRED),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 0

    def test_required_field_empty_string_returns_issue(
        self, validator: RequiredFieldValidator
    ) -> None:
        """Empty string treated as missing."""
        row = FileRow(row_number=2, data={"transaction_date": ""})
        field_map = create_field_map([
            create_field_map_field("transaction_date", status=FieldStatus.REQUIRED),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 1


class TestDateFormatValidator:
    @pytest.fixture
    def validator(self) -> DateFormatValidator:
        return DateFormatValidator()

    def test_valid_date_mm_dd_yyyy_passes(self, validator: DateFormatValidator) -> None:
        """MM/DD/YYYY format passes."""
        row = FileRow(row_number=2, data={"transaction_date": "01/15/2026"})
        field_map = create_field_map([
            create_field_map_field("transaction_date", field_type=FieldType.DATE),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 0

    def test_valid_date_yyyy_mm_dd_passes(self, validator: DateFormatValidator) -> None:
        """YYYY-MM-DD format passes."""
        row = FileRow(row_number=2, data={"transaction_date": "2026-01-15"})
        field_map = create_field_map([
            create_field_map_field("transaction_date", field_type=FieldType.DATE),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 0

    def test_invalid_date_format_returns_issue(
        self, validator: DateFormatValidator
    ) -> None:
        """Invalid format creates issue."""
        row = FileRow(row_number=2, data={"transaction_date": "not-a-date"})
        field_map = create_field_map([
            create_field_map_field("transaction_date", field_type=FieldType.DATE),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 1
        assert issues[0].validation_key == "date_format"


class TestNumericFieldValidator:
    @pytest.fixture
    def validator(self) -> NumericFieldValidator:
        return NumericFieldValidator()

    def test_valid_integer_passes(self, validator: NumericFieldValidator) -> None:
        """Integer field passes."""
        row = FileRow(row_number=2, data={"quantity_units_sold": "100"})
        field_map = create_field_map([
            create_field_map_field("quantity_units_sold", field_type=FieldType.INTEGER),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 0

    def test_valid_decimal_passes(self, validator: NumericFieldValidator) -> None:
        """Decimal field passes."""
        row = FileRow(row_number=2, data={"extended_net_price": "1234.56"})
        field_map = create_field_map([
            create_field_map_field("extended_net_price", field_type=FieldType.DECIMAL),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 0

    def test_non_numeric_value_returns_issue(
        self, validator: NumericFieldValidator
    ) -> None:
        """Non-numeric creates issue."""
        row = FileRow(row_number=2, data={"quantity_units_sold": "abc"})
        field_map = create_field_map([
            create_field_map_field("quantity_units_sold", field_type=FieldType.INTEGER),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 1
        assert issues[0].validation_key == "numeric_field"


class TestZipCodeValidator:
    @pytest.fixture
    def validator(self) -> ZipCodeValidator:
        return ZipCodeValidator()

    def test_valid_5_digit_zip_passes(self, validator: ZipCodeValidator) -> None:
        """5-digit ZIP passes."""
        row = FileRow(row_number=2, data={"selling_branch_zip_code": "12345"})
        field_map = create_field_map([
            create_field_map_field("selling_branch_zip_code"),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 0

    def test_valid_9_digit_zip_passes(self, validator: ZipCodeValidator) -> None:
        """9-digit ZIP (with hyphen) passes."""
        row = FileRow(row_number=2, data={"selling_branch_zip_code": "12345-6789"})
        field_map = create_field_map([
            create_field_map_field("selling_branch_zip_code"),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 0

    def test_invalid_zip_returns_issue(self, validator: ZipCodeValidator) -> None:
        """Invalid ZIP creates issue."""
        row = FileRow(row_number=2, data={"selling_branch_zip_code": "1234"})
        field_map = create_field_map([
            create_field_map_field("selling_branch_zip_code"),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 1
        assert issues[0].validation_key == "zip_code"


class TestPriceCalculationValidator:
    @pytest.fixture
    def validator(self) -> PriceCalculationValidator:
        return PriceCalculationValidator()

    def test_correct_calculation_passes(
        self, validator: PriceCalculationValidator
    ) -> None:
        """qty × unit_cost = extended_price."""
        row = FileRow(
            row_number=2,
            data={
                "quantity_units_sold": "10",
                "distributor_unit_cost": "5.00",
                "extended_net_price": "50.00",
            },
        )
        field_map = create_field_map([
            create_field_map_field("quantity_units_sold", field_type=FieldType.INTEGER),
            create_field_map_field(
                "distributor_unit_cost", field_type=FieldType.DECIMAL
            ),
            create_field_map_field("extended_net_price", field_type=FieldType.DECIMAL),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 0

    def test_incorrect_calculation_returns_issue(
        self, validator: PriceCalculationValidator
    ) -> None:
        """Mismatch creates issue."""
        row = FileRow(
            row_number=2,
            data={
                "quantity_units_sold": "10",
                "distributor_unit_cost": "5.00",
                "extended_net_price": "100.00",
            },
        )
        field_map = create_field_map([
            create_field_map_field("quantity_units_sold", field_type=FieldType.INTEGER),
            create_field_map_field(
                "distributor_unit_cost", field_type=FieldType.DECIMAL
            ),
            create_field_map_field("extended_net_price", field_type=FieldType.DECIMAL),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 1
        assert issues[0].validation_key == "price_calculation"

    def test_missing_fields_skips_validation(
        self, validator: PriceCalculationValidator
    ) -> None:
        """Skip if fields missing."""
        row = FileRow(
            row_number=2,
            data={"quantity_units_sold": "10"},
        )
        field_map = create_field_map([
            create_field_map_field("quantity_units_sold", field_type=FieldType.INTEGER),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 0


class TestFutureDateValidator:
    @pytest.fixture
    def validator(self) -> FutureDateValidator:
        return FutureDateValidator()

    def test_past_date_passes(self, validator: FutureDateValidator) -> None:
        """Past date passes."""
        past_date = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
        row = FileRow(row_number=2, data={"transaction_date": past_date})
        field_map = create_field_map([
            create_field_map_field("transaction_date", field_type=FieldType.DATE),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 0

    def test_today_passes(self, validator: FutureDateValidator) -> None:
        """Today's date passes."""
        today = date.today().strftime("%Y-%m-%d")
        row = FileRow(row_number=2, data={"transaction_date": today})
        field_map = create_field_map([
            create_field_map_field("transaction_date", field_type=FieldType.DATE),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 0

    def test_future_date_returns_issue(self, validator: FutureDateValidator) -> None:
        """Future date creates issue."""
        future_date = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
        row = FileRow(row_number=2, data={"transaction_date": future_date})
        field_map = create_field_map([
            create_field_map_field("transaction_date", field_type=FieldType.DATE),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 1
        assert issues[0].validation_key == "future_date"


class TestCatalogNumberFormatValidator:
    @pytest.fixture
    def validator(self) -> CatalogNumberFormatValidator:
        return CatalogNumberFormatValidator()

    def test_catalog_with_prefix_returns_warning(
        self, validator: CatalogNumberFormatValidator
    ) -> None:
        """Detected prefix creates warning."""
        row = FileRow(row_number=2, data={"manufacturer_catalog_number": "ABC-12345"})
        field_map = create_field_map([
            create_field_map_field("manufacturer_catalog_number"),
        ])
        # Simulate prefix patterns
        prefix_patterns = ["ABC-", "XYZ-"]

        issues = validator.validate(row, field_map, prefix_patterns=prefix_patterns)

        assert len(issues) == 1
        assert issues[0].validation_key == "catalog_number_format"
        assert validator.validation_type == ValidationType.VALIDATION_WARNING


class TestLotOrderDetectionValidator:
    @pytest.fixture
    def validator(self) -> LotOrderDetectionValidator:
        return LotOrderDetectionValidator()

    def test_lot_order_type_returns_warning(
        self, validator: LotOrderDetectionValidator
    ) -> None:
        """LST/DIRECT_SHIP/etc creates warning."""
        row = FileRow(row_number=2, data={"order_type": "LOT"})
        field_map = create_field_map([
            create_field_map_field("order_type"),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 1
        assert issues[0].validation_key == "lot_order_detection"
        assert validator.validation_type == ValidationType.VALIDATION_WARNING


class TestShipFromLocationValidator:
    @pytest.fixture
    def validator(self) -> ShipFromLocationValidator:
        return ShipFromLocationValidator()

    def test_different_ship_from_returns_warning(
        self, validator: ShipFromLocationValidator
    ) -> None:
        """Different location creates warning."""
        row = FileRow(
            row_number=2,
            data={
                "selling_branch_number": "001",
                "shipping_branch_number": "002",
            },
        )
        field_map = create_field_map([
            create_field_map_field("selling_branch_number"),
            create_field_map_field("shipping_branch_number"),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 1
        assert issues[0].validation_key == "ship_from_location"
        assert validator.validation_type == ValidationType.VALIDATION_WARNING


class TestLostFlagValidator:
    @pytest.fixture
    def validator(self) -> LostFlagValidator:
        return LostFlagValidator()

    def test_lost_flag_present_returns_warning(
        self, validator: LostFlagValidator
    ) -> None:
        """Lost flag creates warning."""
        row = FileRow(row_number=2, data={"lost_flag": "Y"})
        field_map = create_field_map([
            create_field_map_field("lost_flag"),
        ])

        issues = validator.validate(row, field_map)

        assert len(issues) == 1
        assert issues[0].validation_key == "lost_flag"
        assert validator.validation_type == ValidationType.VALIDATION_WARNING
