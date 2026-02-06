import hashlib
import hmac
import time


class WebhookSignatureError(Exception):
    """Base exception for webhook signature errors."""


class MissingSignatureError(WebhookSignatureError):
    """Raised when signature header is missing or malformed."""


class InvalidSignatureError(WebhookSignatureError):
    """Raised when signature verification fails."""


class SignatureExpiredError(WebhookSignatureError):
    """Raised when signature timestamp is too old."""


def parse_signature_header(header: str) -> tuple[int, str]:
    """
    Parse WorkOS-Signature header into timestamp and signature hash.

    Header format: "t=1706371200000, v1=abc123def456"

    Returns:
        Tuple of (timestamp_ms, signature_hash)

    Raises:
        MissingSignatureError: If header is empty or missing required parts
    """
    if not header:
        raise MissingSignatureError("Signature header is empty")

    timestamp: int | None = None
    signature: str | None = None

    parts = header.split(",")
    for part in parts:
        part = part.strip()
        if part.startswith("t="):
            timestamp = int(part[2:])
        elif part.startswith("v1="):
            signature = part[3:]

    if timestamp is None:
        raise MissingSignatureError("Missing timestamp in signature header")

    if signature is None:
        raise MissingSignatureError("Missing signature hash in signature header")

    return timestamp, signature


def verify_signature(
    payload: bytes,
    header: str,
    secret: str,
    tolerance_seconds: int = 300,
) -> bool:
    """
    Verify WorkOS webhook signature.

    Args:
        payload: Raw request body as bytes
        header: WorkOS-Signature header value
        secret: Webhook secret from WorkOS dashboard
        tolerance_seconds: Maximum age of signature in seconds (default 5 min)

    Returns:
        True if signature is valid

    Raises:
        MissingSignatureError: If header is missing or malformed
        InvalidSignatureError: If signature doesn't match
        SignatureExpiredError: If timestamp is too old
    """
    timestamp_ms, expected_signature = parse_signature_header(header)

    # Check timestamp age
    current_time_ms = int(time.time() * 1000)
    age_seconds = (current_time_ms - timestamp_ms) / 1000

    if age_seconds > tolerance_seconds:
        raise SignatureExpiredError(
            f"Signature expired: {age_seconds:.0f}s old (max {tolerance_seconds}s)"
        )

    # Compute expected signature
    message = f"{timestamp_ms}.{payload.decode()}"
    computed_signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(computed_signature, expected_signature):
        raise InvalidSignatureError("Signature verification failed")

    return True
