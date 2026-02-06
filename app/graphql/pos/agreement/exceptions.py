from app.errors.base_exception import BaseException


class AgreementError(BaseException):
    """Base exception for agreement operations."""


class S3ConnectionError(AgreementError):
    """S3 connection failed."""


class S3UploadError(AgreementError):
    """S3 upload failed."""


class AgreementNotFoundError(AgreementError):
    """Agreement not found for deletion."""


class ConnectionNotAcceptedError(AgreementError):
    """Connection status is not ACCEPTED."""
