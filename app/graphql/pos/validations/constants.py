BLOCKING_VALIDATION_KEYS = [
    "required_field",
    "date_format",
    "numeric_field",
    "zip_code",
    "price_calculation",
    "future_date",
    "line_level_data",
]

# Maps (validation_key, column_name) to human-readable title
# Use (validation_key, None) for column-agnostic titles
ISSUE_TITLE_MAPPING: dict[tuple[str, str | None], str] = {
    # Required field validations
    ("required_field", "selling_branch_zip_code"): "Selling branch zip code missing",
    ("required_field", "manufacturer_catalog_number"): "No product identifier found",
    ("required_field", "transaction_date"): "Transaction date missing",
    ("required_field", "quantity_units_sold"): "Quantity missing",
    ("required_field", "distributor_unit_cost"): "Unit cost missing",
    ("required_field", "extended_net_price"): "Extended price missing",
    # Date format validations
    ("date_format", None): "Invalid date format",
    # Numeric field validations
    ("numeric_field", None): "Invalid numeric value",
    # ZIP code validations
    ("zip_code", "selling_branch_zip_code"): "Invalid ZIP code format",
    ("zip_code", "shipping_branch_zip_code"): "Invalid shipping ZIP code format",
    ("zip_code", "bill_to_branch_zip_code"): "Invalid bill-to ZIP code format",
    # Price calculation
    ("price_calculation", None): "Price calculation mismatch",
    # Future date
    ("future_date", None): "Future date not allowed",
    # Line level data
    ("line_level_data", None): "Line-level data required",
    # Warning validations
    ("lot_order_detection", None): "Lot/special order detected",
    ("ship_from_location", None): "Ship-from location differs",
    ("lost_flag", None): "Lost flag is set",
    ("catalog_number_format", None): "Catalog number format warning",
}


def get_issue_title(validation_key: str, column_name: str | None) -> str:
    # Try exact match first
    if (validation_key, column_name) in ISSUE_TITLE_MAPPING:
        return ISSUE_TITLE_MAPPING[(validation_key, column_name)]

    # Try column-agnostic match
    if (validation_key, None) in ISSUE_TITLE_MAPPING:
        return ISSUE_TITLE_MAPPING[(validation_key, None)]

    # Fallback: generate from validation_key
    return validation_key.replace("_", " ").title() + " validation issue"
