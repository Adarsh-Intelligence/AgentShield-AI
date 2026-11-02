from __future__ import annotations

from typing import Optional
from backend.app.core.exceptions import BadRequestException
from backend.app.models.agent import Agent
from backend.app.providers.base import BaseLLMProvider
from backend.app.providers.groq_provider import GroqProvider
from backend.app.providers.mock_provider import MockProvider
from backend.app.providers.ollama_provider import OllamaProvider
from backend.app.providers.openai_provider import OpenAICompatibleProvider
from backend.app.utils.encryption import encryption_service
from backend.app.utils.ssrf import validate_outbound_url


class ProviderFactory:
    @staticmethod
    def get_provider_for_agent(
        agent: Agent,
        api_key_override: Optional[str] = None,
        bypass_ssrf_for_tests: bool = False,
    ) -> BaseLLMProvider:
        # Decrypt stored API key if present
        api_key = api_key_override
        if not api_key and agent.credential:
            api_key = encryption_service.decrypt(agent.credential.encrypted_api_key)

        provider_type = agent.provider_type.lower()

        if provider_type == "mock":
            return MockProvider(
                api_endpoint=agent.api_endpoint,
                model_name=agent.model_name,
                api_key=api_key,
                timeout_seconds=agent.timeout_seconds,
                custom_headers=agent.custom_headers,
            )

        # Validate outbound URL against SSRF
        if not bypass_ssrf_for_tests:
            validate_outbound_url(agent.api_endpoint)

        if provider_type == "groq":
            return GroqProvider(
                api_endpoint=agent.api_endpoint,
                model_name=agent.model_name,
                api_key=api_key,
                timeout_seconds=agent.timeout_seconds,
                custom_headers=agent.custom_headers,
            )
        elif provider_type == "ollama":
            return OllamaProvider(
                api_endpoint=agent.api_endpoint,
                model_name=agent.model_name,
                api_key=api_key,
                timeout_seconds=agent.timeout_seconds,
                custom_headers=agent.custom_headers,
            )
        elif provider_type == "openai_compatible":
            return OpenAICompatibleProvider(
                api_endpoint=agent.api_endpoint,
                model_name=agent.model_name,
                api_key=api_key,
                timeout_seconds=agent.timeout_seconds,
                custom_headers=agent.custom_headers,
            )
        else:
            raise BadRequestException(f"Unsupported provider type: '{provider_type}'")

