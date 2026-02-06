from enum import StrEnum


class FieldMapType(StrEnum):
    POS = "pos"
    POT = "pot"


class FieldMapDirection(StrEnum):
    SEND = "send"
    RECEIVE = "receive"


class FieldStatus(StrEnum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    HIGHLY_SUGGESTED = "highly_suggested"
    ONE_REQUIRED = "one_required"
    CAN_CALCULATE = "can_calculate"


class FieldType(StrEnum):
    TEXT = "text"
    DATE = "date"
    DECIMAL = "decimal"
    INTEGER = "integer"


class FieldCategory(StrEnum):
    TRANSACTION = "transaction"
    SELLING_BRANCH = "selling_branch"
    TERRITORY = "territory"
    SHIPPING_BRANCH = "shipping_branch"
    BILL_TO = "bill_to"
    PRODUCT_IDENTIFICATION = "product_identification"
    QUANTITY_PRICING = "quantity_pricing"
    CUSTOM_COLUMNS = "custom_columns"
