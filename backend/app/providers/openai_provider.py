from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional
import httpx
from backend.app.core.exceptions import ProviderException
from backend.app.providers.base import BaseLLMProvider, ProviderResponse, ToolCall


class OpenAICompatibleProvider(BaseLLMProvider):
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        url = self.api_endpoint
        if not url.endswith("/chat/completions"):
            url = f"{url}/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Content-Type": "application/json",
            **self.custom_headers,
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools

        start_time = time.perf_counter()
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                latency_ms = (time.perf_counter() - start_time) * 1000.0

                if response.status_code >= 400:
                    raise ProviderException(
                        "openai_compatible",
                        f"HTTP {response.status_code}: {response.text}",
                    )

                data = response.json()
            except httpx.RequestError as exc:
                raise ProviderException("openai_compatible", f"Connection error: {exc}")

        choices = data.get("choices", [])
        if not choices:
            return ProviderResponse(
                text="",
                latency_ms=latency_ms,
                raw_response=data,
            )

        message = choices[0].get("message", {})
        content = message.get("content") or ""

        tool_calls: List[ToolCall] = []
        if "tool_calls" in message and message["tool_calls"]:
            for tc in message["tool_calls"]:
                func = tc.get("function", {})
                name = func.get("name", "")
                args_str = func.get("arguments", "{}")
                try:
                    args = json.loads(args_str) if isinstance(args_str, str) else args_str
                except Exception:
                    args = {"raw": args_str}
                tool_calls.append(ToolCall(name=name, arguments=args))

        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

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
        return await self.generate(prompt="Ping test. Reply with 'pong'.")

