from __future__ import annotations

import base64
import hashlib
from cryptography.fernet import Fernet
from backend.app.config import settings


def _derive_fernet_key(raw_key: str) -> bytes:
    """Ensure the key is a valid 32-byte urlsafe base64 string for Fernet."""
    try:
        # Check if already valid base64 32 bytes
        decoded = base64.urlsafe_b64decode(raw_key)
        if len(decoded) == 32:
            return raw_key.encode("utf-8")
    except Exception:
        pass
    # Hash raw key to 32 bytes and base64-encode
    digest = hashlib.sha256(raw_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


class EncryptionService:
    def __init__(self, key: str | None = None) -> None:
        raw = key or settings.ENCRYPTION_KEY
        self._fernet_key = _derive_fernet_key(raw)
        self._fernet = Fernet(self._fernet_key)

    def encrypt(self, plain_text: str) -> str:
        if not plain_text:
            return ""
        encrypted_bytes = self._fernet.encrypt(plain_text.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt(self, cipher_text: str) -> str:
        if not cipher_text:
            return ""
        decrypted_bytes = self._fernet.decrypt(cipher_text.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")


encryption_service = EncryptionService()

