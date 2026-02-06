from app.graphql.pos.field_map.models.field_map import FieldMap
from app.graphql.pos.validations.models.enums import ValidationType
from app.graphql.pos.validations.services.file_reader_service import FileRow
from app.graphql.pos.validations.services.validators.base import (
    BaseValidator,
    ValidationIssue,
)


class ShipFromLocationValidator(BaseValidator):
    validation_key = "ship_from_location"
    validation_type = ValidationType.VALIDATION_WARNING

    def validate(self, row: FileRow, field_map: FieldMap) -> list[ValidationIssue]:
        selling_branch = row.data.get("selling_branch_number")
        shipping_branch = row.data.get("shipping_branch_number")

        if selling_branch is None or shipping_branch is None:
            return []

        str_selling = str(selling_branch).strip()
        str_shipping = str(shipping_branch).strip()

        if str_selling and str_shipping and str_selling != str_shipping:
            return [
                ValidationIssue(
                    row_number=row.row_number,
                    column_name="shipping_branch_number",
                    validation_key=self.validation_key,
                    message=(
                        f"Ship-from location differs from selling branch: "
                        f"selling={selling_branch}, shipping={shipping_branch}"
                    ),
                    row_data=row.data,
                )
            ]

        return []
