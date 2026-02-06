from enum import StrEnum


class PosPreferenceKey(StrEnum):
    SEND_METHOD = "send_method"
    RECEIVING_METHOD = "receiving_method"
    ROUTING_METHOD = "routing_method"
    MANUFACTURER_COLUMN = "manufacturer_column"
    MANUFACTURER_PART_NUMBER_PREFIX_REMOVAL = "manufacturer_part_number_prefix_removal"


class TransferMethod(StrEnum):
    UPLOAD_FILE = "upload_file"
    API = "api"
    SFTP = "sftp"
    EMAIL = "email"


class RoutingMethod(StrEnum):
    BY_COLUMN = "by_column"
    BY_FILE = "by_file"
