from __future__ import annotations

from typing import Any, Dict, Optional
from backend.app.config import settings
from backend.app.providers.openai_provider import OpenAICompatibleProvider


class GroqProvider(OpenAICompatibleProvider):
    def __init__(
        self,
        api_endpoint: Optional[str] = None,
        model_name: str = "llama3-70b-8192",
        api_key: Optional[str] = None,
        timeout_seconds: int = 30,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        endpoint = api_endpoint or "https://api.groq.com/openai/v1"
        key = api_key or settings.GROQ_API_KEY
        super().__init__(
            api_endpoint=endpoint,
            model_name=model_name,
            api_key=key,
            timeout_seconds=timeout_seconds,
            custom_headers=custom_headers,
        )

