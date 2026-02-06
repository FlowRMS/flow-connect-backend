from decimal import Decimal, InvalidOperation

from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validators.base import (
    BaseValidator,
    ValidationIssue,
)

TOLERANCE = Decimal("0.01")


class PriceCalculationValidator(BaseValidator):
    validation_key = "price_calculation"
    validation_type = ValidationType.STANDARD_VALIDATION

    def validate(self, row: FileRow, field_map: FieldMap) -> list[ValidationIssue]:
        qty_value = row.data.get("quantity_units_sold")
        unit_cost_value = row.data.get("distributor_unit_cost")
        extended_price_value = row.data.get("extended_net_price")

        if not all([qty_value, unit_cost_value, extended_price_value]):
            return []

        try:
            qty = Decimal(str(qty_value))
            unit_cost = Decimal(str(unit_cost_value))
            extended_price = Decimal(str(extended_price_value))
        except (InvalidOperation, ValueError):
            return []

        expected = qty * unit_cost
        diff = abs(expected - extended_price)

        if diff > TOLERANCE:
            return [
                ValidationIssue(
                    row_number=row.row_number,
                    column_name="extended_net_price",
                    validation_key=self.validation_key,
                    message=(
                        f"Price calculation mismatch: {qty} × {unit_cost} = {expected}, "
                        f"but extended_net_price is {extended_price}"
                    ),
                    row_data=row.data,
                )
            ]

        return []
