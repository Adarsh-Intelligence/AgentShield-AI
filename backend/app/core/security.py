from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, Optional, Set
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from backend.app.config import settings
from backend.app.core.exceptions import UnauthorizedException


class UserRole(str, Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"


_hasher = PasswordHasher()

# In-memory revocation set for revoked tokens (can also be backed by Redis)
_REVOKED_TOKENS: Set[str] = set()


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty.")
    return _hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    try:
        return _hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError):
        return False
    except Exception:
        return False


def create_jwt_token(
    payload: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access",
) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        if token_type == "access":
            expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "type": token_type,
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
    if is_token_revoked(token):
        raise UnauthorizedException("Token has been revoked.")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if expected_type and payload.get("type") != expected_type:
            raise UnauthorizedException(f"Invalid token type: expected '{expected_type}'")
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token has expired.")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Invalid token signature or payload.")


def revoke_token(token: str) -> None:
    _REVOKED_TOKENS.add(token)


def is_token_revoked(token: str) -> bool:
    return token in _REVOKED_TOKENS

