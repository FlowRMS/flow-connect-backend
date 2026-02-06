import re
from dataclasses import dataclass

from app.graphql.pos.field_map.models.field_map_enums import (
    FieldCategory,
    FieldStatus,
    FieldType,
)


@dataclass(frozen=True)
class CategoryConfig:
    name: str
    description: str
    order: int
    visible: bool = True


@dataclass(frozen=True)
class DefaultFieldConfig:
    key: str
    category: FieldCategory
    standard_field_name: str
    description: str
    status: FieldStatus
    field_type: FieldType
    preferred: bool = False
    order: int = 0


CATEGORY_CONFIG: dict[FieldCategory, CategoryConfig] = {
    FieldCategory.TRANSACTION: CategoryConfig(
        name="Transaction",
        description="Transaction-level information",
        order=1,
    ),
    FieldCategory.SELLING_BRANCH: CategoryConfig(
        name="Selling Branch (Credit Owner)",
        description="Selling branch details",
        order=2,
    ),
    FieldCategory.TERRITORY: CategoryConfig(
        name="Territory (ZIP Codes)",
        description="Geographic territory info",
        order=3,
    ),
    FieldCategory.SHIPPING_BRANCH: CategoryConfig(
        name="Shipping Branch (Fulfillment)",
        description="Shipping/fulfillment location",
        order=4,
    ),
    FieldCategory.BILL_TO: CategoryConfig(
        name="Bill-To (Billing Context)",
        description="Billing entity information",
        order=5,
    ),
    FieldCategory.PRODUCT_IDENTIFICATION: CategoryConfig(
        name="Product Identification",
        description="Product identifiers",
        order=6,
    ),
    FieldCategory.QUANTITY_PRICING: CategoryConfig(
        name="Quantity & Pricing",
        description="Quantity and pricing data",
        order=7,
    ),
    FieldCategory.CUSTOM_COLUMNS: CategoryConfig(
        name="Custom Columns",
        description="User-defined custom fields",
        order=8,
    ),
}


DEFAULT_FIELDS: list[DefaultFieldConfig] = [
    # Transaction
    DefaultFieldConfig(
        key="transaction_date",
        category=FieldCategory.TRANSACTION,
        standard_field_name="Transaction Date",
        description="The date of the transaction or invoice.",
        status=FieldStatus.REQUIRED,
        field_type=FieldType.DATE,
        order=1,
    ),
    DefaultFieldConfig(
        key="order_type",
        category=FieldCategory.TRANSACTION,
        standard_field_name="Order Type",
        description=(
            "Identifies the type of order for proper classification "
            "(e.g., STANDARD, LOT, DIRECT_SHIP, PROJECT). Lot and direct-ship orders "
            "may require separate handling for rep compensation."
        ),
        status=FieldStatus.OPTIONAL,
        field_type=FieldType.TEXT,
        order=2,
    ),
    # Selling Branch (Credit Owner)
    DefaultFieldConfig(
        key="selling_branch_number",
        category=FieldCategory.SELLING_BRANCH,
        standard_field_name="Selling Branch #",
        description=(
            "The internal branch number or identifier for the selling location. "
            "Highly recommended for clarity and auditability."
        ),
        status=FieldStatus.HIGHLY_SUGGESTED,
        field_type=FieldType.TEXT,
        order=1,
    ),
    DefaultFieldConfig(
        key="selling_branch_name_city",
        category=FieldCategory.SELLING_BRANCH,
        standard_field_name="Selling Branch Name / City",
        description=(
            "The name or city of the selling branch. "
            "Highly recommended for clarity and auditability."
        ),
        status=FieldStatus.HIGHLY_SUGGESTED,
        field_type=FieldType.TEXT,
        order=2,
    ),
    # Territory (ZIP Codes)
    DefaultFieldConfig(
        key="selling_branch_zip_code",
        category=FieldCategory.TERRITORY,
        standard_field_name="Selling Branch Zip Code",
        description=(
            "For POS reporting, this is the ZIP code of the branch that sold the "
            "material to the customer. Required if Customer Zip Code is not provided. "
            "NEMRA defines 'place of purchase' as either the distributor branch "
            "location and/or the customer's zip code."
        ),
        status=FieldStatus.ONE_REQUIRED,
        field_type=FieldType.TEXT,
        order=1,
    ),
    # Shipping Branch (Fulfillment)
    DefaultFieldConfig(
        key="shipping_branch_number",
        category=FieldCategory.SHIPPING_BRANCH,
        standard_field_name="Shipping Branch #",
        description=(
            "The internal branch number or identifier for the shipping/fulfillment "
            "location. Where the order ships from."
        ),
        status=FieldStatus.HIGHLY_SUGGESTED,
        field_type=FieldType.TEXT,
        order=1,
    ),
    DefaultFieldConfig(
        key="shipping_branch_name_city",
        category=FieldCategory.SHIPPING_BRANCH,
        standard_field_name="Shipping Branch Name / City",
        description=(
            "The name or city of the shipping branch. Where the order ships from."
        ),
        status=FieldStatus.HIGHLY_SUGGESTED,
        field_type=FieldType.TEXT,
        order=2,
    ),
    DefaultFieldConfig(
        key="shipping_branch_zip_code",
        category=FieldCategory.SHIPPING_BRANCH,
        standard_field_name="Shipping Branch Zip Code",
        description="The ZIP code of the branch that shipped the order.",
        status=FieldStatus.OPTIONAL,
        field_type=FieldType.TEXT,
        order=3,
    ),
    # Bill-To (Billing Context)
    DefaultFieldConfig(
        key="bill_to_account_code",
        category=FieldCategory.BILL_TO,
        standard_field_name="Bill-To Account / Code",
        description=(
            "The account number or code for the billing entity. "
            "Never used for rep credit, but critical for audits."
        ),
        status=FieldStatus.HIGHLY_SUGGESTED,
        field_type=FieldType.TEXT,
        order=1,
    ),
    DefaultFieldConfig(
        key="bill_to_branch_name_city",
        category=FieldCategory.BILL_TO,
        standard_field_name="Bill-To Branch Name / City",
        description=(
            "The name or city of the bill-to branch. "
            "Never used for rep credit, but critical for audits."
        ),
        status=FieldStatus.HIGHLY_SUGGESTED,
        field_type=FieldType.TEXT,
        order=2,
    ),
    DefaultFieldConfig(
        key="bill_to_branch_zip_code",
        category=FieldCategory.BILL_TO,
        standard_field_name="Bill-To Branch Zip Code",
        description="The ZIP code of the bill-to branch location.",
        status=FieldStatus.OPTIONAL,
        field_type=FieldType.TEXT,
        order=3,
    ),
    # Product Identification
    DefaultFieldConfig(
        key="manufacturer_catalog_number",
        category=FieldCategory.PRODUCT_IDENTIFICATION,
        standard_field_name="Manufacturer Catalog #",
        description=(
            "The manufacturer's catalog number for the product. "
            "Preferred product identifier; UPC recommended as cross-reference. "
            "Provide at least ONE product identifier."
        ),
        status=FieldStatus.ONE_REQUIRED,
        field_type=FieldType.TEXT,
        preferred=True,
        order=1,
    ),
    DefaultFieldConfig(
        key="manufacturer_sku_number",
        category=FieldCategory.PRODUCT_IDENTIFICATION,
        standard_field_name="Manufacturer SKU #",
        description=(
            "The manufacturer's SKU number for the product. "
            "Provide at least ONE product identifier."
        ),
        status=FieldStatus.ONE_REQUIRED,
        field_type=FieldType.TEXT,
        order=2,
    ),
    DefaultFieldConfig(
        key="upc_code",
        category=FieldCategory.PRODUCT_IDENTIFICATION,
        standard_field_name="UPC Code",
        description=(
            "The Universal Product Code for the product. "
            "Recommended as cross-reference. Provide at least ONE product identifier."
        ),
        status=FieldStatus.ONE_REQUIRED,
        field_type=FieldType.TEXT,
        order=3,
    ),
    DefaultFieldConfig(
        key="unit_of_measure",
        category=FieldCategory.PRODUCT_IDENTIFICATION,
        standard_field_name="Unit of Measure",
        description="The unit of measure for the product (e.g., EA, BOX, CASE).",
        status=FieldStatus.HIGHLY_SUGGESTED,
        field_type=FieldType.TEXT,
        order=4,
    ),
    # Quantity & Pricing
    DefaultFieldConfig(
        key="quantity_units_sold",
        category=FieldCategory.QUANTITY_PRICING,
        standard_field_name="Quantity (# of Units Sold)",
        description=(
            "The number of units sold in the transaction. Extended Net Price is "
            "required for commission calculations. You can either map Extended Net "
            "Price directly (Qty and Unit Cost become optional) or map both Quantity "
            "and Unit Cost (Extended Price will be calculated)."
        ),
        status=FieldStatus.HIGHLY_SUGGESTED,
        field_type=FieldType.INTEGER,
        order=1,
    ),
    DefaultFieldConfig(
        key="distributor_unit_cost",
        category=FieldCategory.QUANTITY_PRICING,
        standard_field_name="Distributor Unit Cost",
        description=(
            "The unit cost/price from the distributor. Extended Net Price is required "
            "for commission calculations. You can either map Extended Net Price "
            "directly (Qty and Unit Cost become optional) or map both Quantity and "
            "Unit Cost (Extended Price will be calculated)."
        ),
        status=FieldStatus.HIGHLY_SUGGESTED,
        field_type=FieldType.DECIMAL,
        order=2,
    ),
    DefaultFieldConfig(
        key="extended_net_price",
        category=FieldCategory.QUANTITY_PRICING,
        standard_field_name="Extended Net Price",
        description=(
            "The total net price for the line item (Qty × Unit Cost). This is the "
            "goal for commission calculations. You can either map Extended Net Price "
            "directly (Qty and Unit Cost become optional) or map both Quantity and "
            "Unit Cost (Extended Price will be calculated)."
        ),
        status=FieldStatus.CAN_CALCULATE,
        field_type=FieldType.DECIMAL,
        preferred=True,
        order=3,
    ),
]

DEFAULT_FIELD_KEYS: set[str] = {field.key for field in DEFAULT_FIELDS}


def get_category_config(category: FieldCategory) -> CategoryConfig | None:
    return CATEGORY_CONFIG.get(category)


def get_default_fields() -> list[DefaultFieldConfig]:
    return DEFAULT_FIELDS


def get_default_field_by_key(key: str) -> DefaultFieldConfig | None:
    for field in DEFAULT_FIELDS:
        if field.key == key:
            return field
    return None


def generate_field_key(name: str) -> str:
    """Generate a key from a field name by slugifying it."""
    # Lowercase and replace non-alphanumeric with underscores
    key = name.lower()
    key = re.sub(r"[^a-z0-9]+", "_", key)
    # Remove leading/trailing underscores
    key = key.strip("_")
    # Collapse multiple underscores
    key = re.sub(r"_+", "_", key)
    return key


def generate_unique_field_key(name: str, existing_keys: set[str]) -> str:
    """Generate a unique key, adding suffix if collision."""
    base_key = generate_field_key(name)
    if base_key not in existing_keys:
        return base_key

    # Add numeric suffix until unique
    counter = 2
    while f"{base_key}_{counter}" in existing_keys:
        counter += 1
    return f"{base_key}_{counter}"
