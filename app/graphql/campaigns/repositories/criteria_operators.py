from datetime import date, datetime
from typing import Any
from uuid import UUID

from commons.db.int_enum import IntEnum as IntEnumColumn
from sqlalchemy import ARRAY, Date, String, Text, func

from app.graphql.campaigns.strawberry.criteria_enums import CriteriaOperator


def is_string_column(column: Any) -> bool:
    try:
        column_type = column.type
        return isinstance(column_type, (String, Text))
    except AttributeError:
        return False


def is_array_column(column: Any) -> bool:
    try:
        column_type = column.type
        return isinstance(column_type, ARRAY)
    except AttributeError:
        return False


def convert_value(column: Any, value: Any) -> Any:
    """
    Convert a value to match the column's expected type.

    Handles:
    - IntEnum columns: converts string enum names to integer values (case-insensitive)
    - Date columns: converts ISO date strings to date objects
    - UUID columns: converts string UUIDs to UUID objects
    - Boolean columns: converts string booleans to bool
    - Lists: recursively converts each element
    """
    if value is None:
        return None

    # Handle lists by converting each element
    if isinstance(value, list):
        return [convert_value(column, v) for v in value]

    # Get the column type from SQLAlchemy
    try:
        column_type = column.type
    except AttributeError:
        return value

    # Handle IntEnum columns (stored as SMALLINT)
    # The IntEnum TypeDecorator uses _enumtype attribute
    if isinstance(column_type, IntEnumColumn):
        enum_class = getattr(column_type, "_enumtype", None)
        if enum_class is None:
            return value
        if isinstance(value, str):
            # Case-insensitive enum lookup
            value_upper = value.upper()
            for member in enum_class:
                if member.name.upper() == value_upper:
                    return member
            # If not found by name, try to parse as integer
            try:
                return enum_class(int(value))
            except (ValueError, KeyError):
                pass
        elif isinstance(value, int):
            try:
                return enum_class(value)
            except (ValueError, KeyError):
                pass
        return value

    # Handle Date columns
    if isinstance(column_type, Date):
        if isinstance(value, str):
            # Empty string should return None for dates
            if not value.strip():
                return None
            # Try ISO format first (YYYY-MM-DD)
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                pass
            # Try other common formats
            for fmt in ["%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"]:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        elif isinstance(value, datetime):
            return value.date()
        elif isinstance(value, date):
            return value
        return value

    # Handle UUID columns
    type_name = type(column_type).__name__
    if type_name == "UUID":
        if isinstance(value, str):
            try:
                return UUID(value)
            except ValueError:
                pass
        return value

    # Handle Boolean columns
    if type_name == "Boolean":
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return bool(value)

    # Handle String columns - ensure string type
    if isinstance(column_type, String) and not isinstance(value, str):
        return str(value)

    return value


def apply_operator(
    column: Any,
    operator: CriteriaOperator,
    value: Any,
) -> Any:
    is_array = is_array_column(column)

    # Handle empty string values
    if isinstance(value, str) and not value.strip():
        # For array columns with empty value, skip the condition
        if is_array:
            return None
        # For date columns, empty string means NULL
        try:
            if isinstance(column.type, Date):
                if operator in (CriteriaOperator.EQUALS, CriteriaOperator.IS_NULL):
                    return column.is_(None)
                elif operator == CriteriaOperator.NOT_EQUALS:
                    return column.isnot(None)
                else:
                    return None
        except AttributeError:
            pass

    # Convert value to match column type (except for NULL checks and string operations)
    if operator not in (
        CriteriaOperator.IS_NULL,
        CriteriaOperator.IS_NOT_NULL,
        CriteriaOperator.CONTAINS,
        CriteriaOperator.NOT_CONTAINS,
    ):
        value = convert_value(column, value)

    # Skip None values that resulted from conversion failures
    if value is None and operator not in (
        CriteriaOperator.IS_NULL,
        CriteriaOperator.IS_NOT_NULL,
    ):
        return None

    # Check if column is string type for case-insensitive comparisons
    is_string = is_string_column(column)

    match operator:
        case CriteriaOperator.EQUALS:
            # Array columns need special handling
            if is_array:
                # For arrays, use array contains operator (@>)
                if isinstance(value, list):
                    return column.contains(value)
                else:
                    # Single value - check if array contains it
                    return column.any(value)
            # Use case-insensitive comparison for string columns
            if is_string and isinstance(value, str):
                return func.lower(column) == func.lower(value)
            return column == value
        case CriteriaOperator.NOT_EQUALS:
            if is_array:
                # For arrays, use NOT array contains operator
                if isinstance(value, list):
                    return ~column.contains(value)
                else:
                    return ~column.any(value)
            if is_string and isinstance(value, str):
                return func.lower(column) != func.lower(value)
            return column != value
        case CriteriaOperator.CONTAINS:
            if is_array:
                # For array columns, check if any element contains the value
                return column.any(value)
            # ilike is already case-insensitive
            return column.ilike(f"%{value}%")
        case CriteriaOperator.NOT_CONTAINS:
            if is_array:
                return ~column.any(value)
            return ~column.ilike(f"%{value}%")
        case CriteriaOperator.GREATER_THAN:
            return column > value
        case CriteriaOperator.LESS_THAN:
            return column < value
        case CriteriaOperator.GREATER_THAN_OR_EQUALS:
            return column >= value
        case CriteriaOperator.LESS_THAN_OR_EQUALS:
            return column <= value
        case CriteriaOperator.IS_NULL:
            return column.is_(None)
        case CriteriaOperator.IS_NOT_NULL:
            return column.isnot(None)
        case CriteriaOperator.IN:
            converted = convert_value(
                column, value if isinstance(value, list) else [value]
            )
            # Use case-insensitive IN for string columns
            if is_string and converted and all(isinstance(v, str) for v in converted):
                return func.lower(column).in_([v.lower() for v in converted])
            return column.in_(converted)
        case CriteriaOperator.NOT_IN:
            converted = convert_value(
                column, value if isinstance(value, list) else [value]
            )
            if is_string and converted and all(isinstance(v, str) for v in converted):
                return ~func.lower(column).in_([v.lower() for v in converted])
            return ~column.in_(converted)
        case _:
            return column == value
