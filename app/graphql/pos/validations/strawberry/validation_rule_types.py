import strawberry

from app.graphql.pos.validations.models.enums import ValidationType

ValidationTypeEnum = strawberry.enum(ValidationType)


@strawberry.type
class ValidationRuleResponse:
    name: str
    description: str
    triggers: list[str]
    validation_type: ValidationType
    enabled: bool

    @staticmethod
    def get_all() -> list["ValidationRuleResponse"]:
        return VALIDATION_RULES


VALIDATION_RULES: list[ValidationRuleResponse] = [
    # Standard Validation (7 items)
    ValidationRuleResponse(
        name="Line-level transaction data required",
        description=(
            "All POS/POT data must be submitted at the individual transaction level. "
            "Aggregated or summarized data (e.g., monthly totals by product, rolled-up "
            "quantities) will be rejected. Each row must represent a single transaction "
            "with its own transaction date, quantity, and pricing."
        ),
        triggers=[
            "Multiple transactions combined into a single row",
            "Monthly or weekly summary data instead of daily transactions",
            "Aggregated quantities across multiple customers or dates",
            "Missing individual transaction identifiers (invoice numbers, dates)",
        ],
        validation_type=ValidationType.STANDARD_VALIDATION,
        enabled=True,
    ),
    ValidationRuleResponse(
        name="Required field validation",
        description="All mandatory NEMRA fields must be present and non-empty.",
        triggers=[],
        validation_type=ValidationType.STANDARD_VALIDATION,
        enabled=True,
    ),
    ValidationRuleResponse(
        name="Date format validation",
        description=(
            "All dates must be valid and in acceptable formats: MM/DD/YYYY, YYYY-MM-DD"
        ),
        triggers=[],
        validation_type=ValidationType.STANDARD_VALIDATION,
        enabled=True,
    ),
    ValidationRuleResponse(
        name="Numeric field validation",
        description="Quantity, unit cost, and extended price must be valid numbers.",
        triggers=[],
        validation_type=ValidationType.STANDARD_VALIDATION,
        enabled=True,
    ),
    ValidationRuleResponse(
        name="ZIP code validation",
        description=(
            "Selling branch ZIP and customer ZIP must be valid 5 or 9 digit formats."
        ),
        triggers=[],
        validation_type=ValidationType.STANDARD_VALIDATION,
        enabled=True,
    ),
    ValidationRuleResponse(
        name="Price calculation check",
        description="Extended price is calculated against quantity × unit cost.",
        triggers=[],
        validation_type=ValidationType.STANDARD_VALIDATION,
        enabled=True,
    ),
    ValidationRuleResponse(
        name="Future date prevention",
        description="Transaction dates cannot be in the future.",
        triggers=[],
        validation_type=ValidationType.STANDARD_VALIDATION,
        enabled=True,
    ),
    # Validation Warnings (4 items)
    ValidationRuleResponse(
        name="Catalog/Part number format check",
        description=(
            "Distributors are encouraged to match manufacturers with the manufacturer's "
            "part number in the format provided in their price/product files, without "
            "appended prefixes. If hyphens or other characters are included in the "
            "manufacturer part number and can be accommodated by your ERP system, they "
            "should be included."
        ),
        triggers=[
            "Part numbers with added distributor prefixes or suffixes",
            "Part numbers without hyphens present in manufacturer format",
            "Truncated part numbers due to ERP field limits",
            "Catalog numbers from a cross-reference matching catalog/product lookup",
        ],
        validation_type=ValidationType.VALIDATION_WARNING,
        enabled=True,
    ),
    ValidationRuleResponse(
        name="Lot order detection",
        description=(
            "Orders with a type of LST, DIRECT_SHIP, PROJECT, or SPECIAL are "
            "automatically marked for manufacturer review. Per NEMRA guidance, these "
            "orders require separate handling for commission calculations."
        ),
        triggers=[],
        validation_type=ValidationType.VALIDATION_WARNING,
        enabled=True,
    ),
    ValidationRuleResponse(
        name="Ship-from location comparison",
        description=(
            "When the ship-from location differs from selling branch, order is flagged "
            "as potential direct ship."
        ),
        triggers=[],
        validation_type=ValidationType.VALIDATION_WARNING,
        enabled=True,
    ),
    ValidationRuleResponse(
        name="Include lost flag",
        description=(
            "Lost orders are included in POS submissions but clearly labeled. They are "
            "never auto-excluded or hidden from manufacturers."
        ),
        triggers=[],
        validation_type=ValidationType.VALIDATION_WARNING,
        enabled=True,
    ),
    # AI-Powered Validation (5 items)
    ValidationRuleResponse(
        name="Duplicate detection",
        description=(
            "AI identifies potential duplicate records based on multiple field matching."
        ),
        triggers=[],
        validation_type=ValidationType.AI_POWERED_VALIDATION,
        enabled=True,
    ),
    ValidationRuleResponse(
        name="Anomaly detection",
        description=(
            "Flags unusual quantities, prices, or patterns that may indicate errors."
        ),
        triggers=[],
        validation_type=ValidationType.AI_POWERED_VALIDATION,
        enabled=True,
    ),
    ValidationRuleResponse(
        name="Catalog number verification",
        description=(
            "AI validates manufacturer part numbers against known manufacturer SKUs."
        ),
        triggers=[],
        validation_type=ValidationType.AI_POWERED_VALIDATION,
        enabled=True,
    ),
    ValidationRuleResponse(
        name="Address standardization",
        description="Validates and normalizes ZIP codes and location data.",
        triggers=[],
        validation_type=ValidationType.AI_POWERED_VALIDATION,
        enabled=True,
    ),
    ValidationRuleResponse(
        name="Historical comparison",
        description=(
            "Compares submissions against historical patterns to catch outliers."
        ),
        triggers=[],
        validation_type=ValidationType.AI_POWERED_VALIDATION,
        enabled=True,
    ),
]
