import hashlib
import hmac
import time

import pytest

from app.webhooks.workos.signature import (
    InvalidSignatureError,
    MissingSignatureError,
    SignatureExpiredError,
    parse_signature_header,
    verify_signature,
)


class TestParseSignatureHeader:
    def test_parse_valid_header(self) -> None:
        """Extract timestamp and hash from valid WorkOS-Signature header."""
        header = "t=1706371200000, v1=abc123def456"
        timestamp, signature = parse_signature_header(header)

        assert timestamp == 1706371200000
        assert signature == "abc123def456"

    def test_parse_header_without_spaces(self) -> None:
        """Handle header format without spaces after comma."""
        header = "t=1706371200000,v1=abc123def456"
        timestamp, signature = parse_signature_header(header)

        assert timestamp == 1706371200000
        assert signature == "abc123def456"

    def test_parse_header_missing_timestamp_raises_error(self) -> None:
        """Raise error when timestamp is missing."""
        header = "v1=abc123def456"

        with pytest.raises(MissingSignatureError) as exc_info:
            parse_signature_header(header)

        assert "timestamp" in str(exc_info.value).lower()

    def test_parse_header_missing_signature_raises_error(self) -> None:
        """Raise error when signature hash is missing."""
        header = "t=1706371200000"

        with pytest.raises(MissingSignatureError) as exc_info:
            parse_signature_header(header)

        assert "signature" in str(exc_info.value).lower()

    def test_parse_empty_header_raises_error(self) -> None:
        """Raise error for empty header."""
        with pytest.raises(MissingSignatureError):
            parse_signature_header("")


class TestVerifySignature:
    @pytest.fixture
    def webhook_secret(self) -> str:
        return "whsec_test_secret_key_12345"

    @pytest.fixture
    def payload(self) -> bytes:
        return b'{"event": "organization.created", "data": {"id": "org_123"}}'

    @staticmethod
    def _generate_valid_signature(
        payload: bytes,
        secret: str,
        timestamp: int | None = None,
    ) -> str:
        """Generate a valid WorkOS signature for testing."""
        if timestamp is None:
            timestamp = int(time.time() * 1000)

        message = f"{timestamp}.{payload.decode()}"
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

        return f"t={timestamp}, v1={signature}"

    def test_verify_valid_signature_returns_true(
        self,
        webhook_secret: str,
        payload: bytes,
    ) -> None:
        """Valid HMAC signature verification succeeds."""
        header = self._generate_valid_signature(payload, webhook_secret)

        result = verify_signature(payload, header, webhook_secret)

        assert result is True

    def test_verify_invalid_signature_raises_error(
        self,
        webhook_secret: str,
        payload: bytes,
    ) -> None:
        """Invalid signature raises InvalidSignatureError."""
        timestamp = int(time.time() * 1000)
        header = f"t={timestamp}, v1=invalid_signature_hash"

        with pytest.raises(InvalidSignatureError):
            verify_signature(payload, header, webhook_secret)

    def test_verify_wrong_secret_raises_error(
        self,
        webhook_secret: str,
        payload: bytes,
    ) -> None:
        """Signature with wrong secret fails verification."""
        header = self._generate_valid_signature(payload, "wrong_secret")

        with pytest.raises(InvalidSignatureError):
            verify_signature(payload, header, webhook_secret)

    def test_verify_tampered_payload_raises_error(
        self,
        webhook_secret: str,
        payload: bytes,
    ) -> None:
        """Tampered payload fails signature verification."""
        header = self._generate_valid_signature(payload, webhook_secret)
        tampered_payload = b'{"event": "organization.deleted", "data": {"id": "org_999"}}'

        with pytest.raises(InvalidSignatureError):
            verify_signature(tampered_payload, header, webhook_secret)

    def test_verify_expired_timestamp_raises_error(
        self,
        webhook_secret: str,
        payload: bytes,
    ) -> None:
        """Timestamp older than tolerance (5 min default) raises error."""
        # 10 minutes ago
        old_timestamp = int((time.time() - 600) * 1000)
        header = self._generate_valid_signature(
            payload,
            webhook_secret,
            timestamp=old_timestamp,
        )

        with pytest.raises(SignatureExpiredError):
            verify_signature(payload, header, webhook_secret, tolerance_seconds=300)

    def test_verify_with_custom_tolerance(
        self,
        webhook_secret: str,
        payload: bytes,
    ) -> None:
        """Custom tolerance allows older timestamps."""
        # 10 minutes ago
        old_timestamp = int((time.time() - 600) * 1000)
        header = self._generate_valid_signature(
            payload,
            webhook_secret,
            timestamp=old_timestamp,
        )

        # 15 minute tolerance should accept 10 minute old signature
        result = verify_signature(
            payload,
            header,
            webhook_secret,
            tolerance_seconds=900,
        )

        assert result is True

    def test_verify_missing_header_raises_error(
        self,
        webhook_secret: str,
        payload: bytes,
    ) -> None:
        """Empty header raises MissingSignatureError."""
        with pytest.raises(MissingSignatureError):
            verify_signature(payload, "", webhook_secret)
