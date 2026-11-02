from __future__ import annotations

import pytest
from backend.app.core.exceptions import SSRFException
from backend.app.utils.encryption import EncryptionService
from backend.app.utils.ssrf import is_ip_private_or_restricted, validate_outbound_url


class TestEncryptionService:
    def test_encrypt_decrypt_roundtrip(self):
        service = EncryptionService()
        secret = "sk-groq-live-key-1234567890abcdef"
        encrypted = service.encrypt(secret)
        assert encrypted != secret
        decrypted = service.decrypt(encrypted)
        assert decrypted == secret

    def test_encrypt_empty_string(self):
        service = EncryptionService()
        assert service.encrypt("") == ""
        assert service.decrypt("") == ""


class TestSSRFProtection:
    def test_private_ip_detection(self):
        assert is_ip_private_or_restricted("127.0.0.1") is True
        assert is_ip_private_or_restricted("10.0.0.5") is True
        assert is_ip_private_or_restricted("172.16.0.1") is True
        assert is_ip_private_or_restricted("192.168.1.100") is True
        assert is_ip_private_or_restricted("169.254.169.254") is True
        assert is_ip_private_or_restricted("::1") is True
        assert is_ip_private_or_restricted("8.8.8.8") is False
        assert is_ip_private_or_restricted("1.1.1.1") is False

    def test_block_metadata_service(self):
        with pytest.raises(SSRFException) as exc_info:
            validate_outbound_url("http://169.254.169.254/latest/meta-data/")
        assert "metadata" in str(exc_info.value.detail).lower()

    def test_block_invalid_scheme(self):
        with pytest.raises(SSRFException) as exc_info:
            validate_outbound_url("file:///etc/passwd")
        assert "Invalid scheme" in str(exc_info.value.detail)

        with pytest.raises(SSRFException) as exc_info:
            validate_outbound_url("gopher://127.0.0.1:6379/")
        assert "Invalid scheme" in str(exc_info.value.detail)

    def test_block_localhost_resolution(self):
        with pytest.raises(SSRFException) as exc_info:
            validate_outbound_url("http://localhost:8000/api", allow_private=False)
        assert "private" in str(exc_info.value.detail).lower() or "loopback" in str(exc_info.value.detail).lower()

