from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToolCall:
    name: str
    arguments: Dict[str, Any]


@dataclass
class ProviderResponse:
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    tool_calls: List[ToolCall] = field(default_factory=list)
    raw_response: Dict[str, Any] = field(default_factory=dict)


class BaseLLMProvider(ABC):
    def __init__(
        self,
        api_endpoint: str,
        model_name: str,
        api_key: Optional[str] = None,
        timeout_seconds: int = 30,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.api_endpoint = api_endpoint.rstrip("/")
        self.model_name = model_name
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.custom_headers = custom_headers or {}

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Sends generation request to the LLM provider."""
        pass

    @abstractmethod
    async def test_connection(self) -> ProviderResponse:
        """Lightweight test to verify provider connectivity and authentication."""
        pass

