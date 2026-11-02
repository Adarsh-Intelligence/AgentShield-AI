from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AgentShieldException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str = "ERROR",
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.code = code
        self.extra = extra or {}


class EntityNotFoundException(AgentShieldException):
    def __init__(self, entity_name: str, entity_id: Any) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} with id '{entity_id}' not found.",
            code="NOT_FOUND",
        )


class UnauthorizedException(AgentShieldException):
    def __init__(self, detail: str = "Could not validate credentials.") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code="UNAUTHORIZED",
        )


class ForbiddenException(AgentShieldException):
    def __init__(self, detail: str = "You do not have permission to access this resource.") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            code="FORBIDDEN",
        )


class BadRequestException(AgentShieldException):
    def __init__(self, detail: str, code: str = "BAD_REQUEST", extra: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            code=code,
            extra=extra,
        )


class ConflictException(AgentShieldException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            code="CONFLICT",
        )


class SSRFException(AgentShieldException):
    def __init__(self, url: str, reason: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Outbound request to '{url}' is blocked due to security policy: {reason}",
            code="SSRF_BLOCKED",
        )


class ProviderException(AgentShieldException):
    def __init__(self, provider: str, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Provider '{provider}' error: {detail}",
            code="PROVIDER_ERROR",
        )

