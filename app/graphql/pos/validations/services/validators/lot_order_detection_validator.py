from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validators.base import (
    BaseValidator,
    ValidationIssue,
)

LOT_ORDER_TYPES = {
    "LOT",
    "LST",
    "DIRECT_SHIP",
    "DIRECTSHIP",
    "PROJECT",
    "SPECIAL",
}


class LotOrderDetectionValidator(BaseValidator):
    validation_key = "lot_order_detection"
    validation_type = ValidationType.VALIDATION_WARNING

    def validate(self, row: FileRow, field_map: FieldMap) -> list[ValidationIssue]:
        order_type_value = row.data.get("order_type")
        if order_type_value is None:
            return []

        str_value = str(order_type_value).upper().strip()
        if str_value in LOT_ORDER_TYPES:
            return [
                ValidationIssue(
                    row_number=row.row_number,
                    column_name="order_type",
                    validation_key=self.validation_key,
                    message=f"Lot/special order type detected: {order_type_value}",
                    row_data=row.data,
                )
            ]

        return []
