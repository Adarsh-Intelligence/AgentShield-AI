from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional
from backend.app.providers.base import BaseLLMProvider, ProviderResponse, ToolCall


class MockProvider(BaseLLMProvider):
    """
    Mock provider for automated unit/integration tests and CI environments.
    Supports predefined responses, regex matching, or custom response callbacks.
    """

    def __init__(
        self,
        api_endpoint: str = "http://mock-llm.local",
        model_name: str = "mock-model",
        api_key: Optional[str] = "mock-key",
        timeout_seconds: int = 5,
        custom_headers: Optional[Dict[str, str]] = None,
        default_response: str = "Mock response from AgentShield AI",
        responses_map: Optional[Dict[str, str]] = None,
        tool_call_map: Optional[Dict[str, List[ToolCall]]] = None,
    ) -> None:
        super().__init__(
            api_endpoint=api_endpoint,
            model_name=model_name,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
            custom_headers=custom_headers,
        )
        self.default_response = default_response
        self.responses_map = responses_map or {}
        self.tool_call_map = tool_call_map or {}
        self.call_history: List[Dict[str, Any]] = []

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        start_time = time.perf_counter()

        self.call_history.append({
            "prompt": prompt,
            "system_prompt": system_prompt,
            "tools": tools,
            "kwargs": kwargs,
        })

        # Match response
        response_text = self.responses_map.get(prompt, self.default_response)
        tool_calls = self.tool_call_map.get(prompt, [])

        # Simulate small latency
        latency_ms = (time.perf_counter() - start_time) * 1000.0 + 5.0
        prompt_tokens = len(prompt.split()) + (len(system_prompt.split()) if system_prompt else 0)
        completion_tokens = len(response_text.split())
        total_tokens = prompt_tokens + completion_tokens

        return ProviderResponse(
            text=response_text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            tool_calls=tool_calls,
            raw_response={
                "mock": True,
                "model": self.model_name,
                "text": response_text,
            },
        )

    async def test_connection(self) -> ProviderResponse:
        return ProviderResponse(
            text="Mock provider connected successfully",
            latency_ms=2.0,
            raw_response={"mock": True, "status": "ok"},
        )

