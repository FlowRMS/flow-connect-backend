from app.errors.base_exception import BaseException


class FieldMapError(BaseException):
    pass


class FieldNotFoundError(FieldMapError):
    pass


class CannotDeleteDefaultFieldError(FieldMapError):
    pass


class CannotEditDefaultFieldError(FieldMapError):
    pass


class LinkedFieldValidationError(FieldMapError):
    pass
