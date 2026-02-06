from app.errors.base_exception import BaseException


class OrganizationAliasError(BaseException):
    pass


class AliasAlreadyExistsError(OrganizationAliasError):
    pass


class OrganizationNotConnectedError(OrganizationAliasError):
    pass


class OrganizationAliasNotFoundError(OrganizationAliasError):
    pass


class CsvParseError(OrganizationAliasError):
    pass


class InvalidCsvColumnsError(CsvParseError):
    pass
