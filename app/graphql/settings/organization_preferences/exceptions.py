from app.errors.base_exception import BaseException


class OrganizationPreferenceError(BaseException):
    pass


class InvalidApplicationError(OrganizationPreferenceError):
    pass


class InvalidPreferenceValueError(OrganizationPreferenceError):
    pass
