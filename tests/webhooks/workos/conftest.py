import hashlib
import hmac
import json
import time


def generate_workos_signature(
    payload: dict,
    secret: str,
    timestamp: int | None = None,
) -> tuple[str, bytes]:
    """
    Generate a valid WorkOS webhook signature for testing.

    This replicates WorkOS's signature format:
    - Header: "t={timestamp_ms}, v1={hmac_sha256_hex}"
    - Message: "{timestamp_ms}.{json_payload}"

    Args:
        payload: The webhook payload dict
        secret: The webhook secret
        timestamp: Optional timestamp in milliseconds (defaults to current time)

    Returns:
        Tuple of (signature_header, payload_bytes)
    """
    if timestamp is None:
        timestamp = int(time.time() * 1000)

    payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
    message = f"{timestamp}.{payload_bytes.decode()}"
    signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()

    return f"t={timestamp}, v1={signature}", payload_bytes
