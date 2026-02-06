from app.errors.base_exception import BaseException


class ExchangeFileError(BaseException):
    """Base exception for exchange file operations."""


class InvalidFileTypeError(ExchangeFileError):
    """File type is not CSV, XLS, or XLSX."""


class DuplicateFileForTargetError(ExchangeFileError):
    """Same file already pending for target organization."""


class ExchangeFileNotFoundError(ExchangeFileError):
    """Exchange file not found."""


class CannotDeleteSentFileError(ExchangeFileError):
    """Cannot delete already sent file."""


class HasBlockingValidationIssuesError(ExchangeFileError):
    """Cannot send files with blocking validation issues."""


class NoPendingFilesError(ExchangeFileError):
    """No pending files to send."""


class ReceivedExchangeFileNotFoundError(ExchangeFileError):
    """Received exchange file not found."""
