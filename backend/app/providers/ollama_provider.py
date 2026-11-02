from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
import httpx
from backend.app.config import settings
from backend.app.core.exceptions import ProviderException
from backend.app.providers.base import BaseLLMProvider, ProviderResponse, ToolCall


class OllamaProvider(BaseLLMProvider):
    def __init__(
        self,
        api_endpoint: Optional[str] = None,
        model_name: str = "llama3",
        api_key: Optional[str] = None,
        timeout_seconds: int = 60,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        endpoint = api_endpoint or settings.OLLAMA_BASE_URL
        super().__init__(
            api_endpoint=endpoint,
            model_name=model_name,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
            custom_headers=custom_headers,
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        url = f"{self.api_endpoint}/api/chat"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        headers = {
            "Content-Type": "application/json",
            **self.custom_headers,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        start_time = time.perf_counter()
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                latency_ms = (time.perf_counter() - start_time) * 1000.0

                if response.status_code >= 400:
                    raise ProviderException(
                        "ollama",
                        f"HTTP {response.status_code}: {response.text}",
                    )

                data = response.json()
            except httpx.RequestError as exc:
                raise ProviderException("ollama", f"Connection error: {exc}")

        message = data.get("message", {})
        content = message.get("content") or ""

        tool_calls: List[ToolCall] = []
        if "tool_calls" in message and message["tool_calls"]:
            for tc in message["tool_calls"]:
                func = tc.get("function", {})
                name = func.get("name", "")
                args = func.get("arguments", {})
                tool_calls.append(ToolCall(name=name, arguments=args))

        prompt_tokens = data.get("prompt_eval_count", len(prompt.split()))
        completion_tokens = data.get("eval_count", len(content.split()))
        total_tokens = prompt_tokens + completion_tokens

        return ProviderResponse(
            text=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            tool_calls=tool_calls,
            raw_response=data,
        )

    async def test_connection(self) -> ProviderResponse:
        url = f"{self.api_endpoint}/api/tags"
        start_time = time.perf_counter()
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            try:
                res = await client.get(url, headers=self.custom_headers)
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                if res.status_code >= 400:
                    raise ProviderException("ollama", f"HTTP {res.status_code}: {res.text}")
                return ProviderResponse(
                    text="Ollama connected successfully",
                    latency_ms=latency_ms,
                    raw_response=res.json(),
                )
            except httpx.RequestError as exc:
                raise ProviderException("ollama", f"Connection error: {exc}")

