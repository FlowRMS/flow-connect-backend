from app.errors.base_exception import BaseException


class ValidationError(BaseException):
    """Base exception for validation operations."""


class PrefixPatternNotFoundError(ValidationError):
    """Prefix pattern not found."""


class PrefixPatternDuplicateError(ValidationError):
    """Prefix pattern name already exists in organization."""


class UserNotAuthenticatedError(ValidationError):
    """User is not authenticated."""


class FieldMapNotFoundError(ValidationError):
    """Field map not found for organization."""
