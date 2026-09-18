"""
LLM Provider Abstraction Layer for CareFlow AI.

Source of truth: docs/safety-privacy.md - Section 62 (AI Model Independence)
and docs/ai-agent-specification.md.
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger("careflow.agent.provider")


@dataclass
class LLMResponse:
    content: str
    raw: Dict[str, Any] = field(default_factory=dict)
    tokens_used: int = 0


class BaseLLMProvider(ABC):
    """
    Abstract interface for LLM backends.
    Allows swappable implementations (Mock, OpenAI, Groq, Ollama, etc.)
    without changing business logic or leaking provider-specific details.
    """

    @abstractmethod
    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> LLMResponse:
        """Synchronous chat completion."""
        pass

    async def acomplete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> LLMResponse:
        """Asynchronous chat completion (defaults to sync wrapper if not overridden)."""
        return self.complete(messages, temperature, max_tokens)


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic, offline LLM provider for tests and local development.
    Requires 0 external network requests and 0 paid credentials.
    """

    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> LLMResponse:
        user_msg = ""
        system_msg = ""
        for m in messages:
            if m.get("role") == "user":
                user_msg = m.get("content", "").lower()
            elif m.get("role") == "system":
                system_msg = m.get("content", "")

        # Default supportive response
        response_text = (
            "Thank you for contacting CareFlow support. I am here to assist you with "
            "appointment logistics, clinic information, and connecting you with healthcare staff. "
            "How can I best assist you today?"
        )

        return LLMResponse(
            content=response_text,
            raw={"provider": "mock", "prompt_length": len(user_msg)},
            tokens_used=len(user_msg.split()) + len(response_text.split()),
        )


class OpenAICompatibleProvider(BaseLLMProvider):
    """
    HTTP REST Client for any OpenAI-compatible Chat Completions API
    (e.g., Groq, OpenAI, Ollama, DeepSeek, LocalAI).
    Uses httpx with connection timeouts and safe error handling.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile",
        base_url: Optional[str] = None,
        timeout: int = 15,
    ):
        self.api_key = api_key or settings.LLM_API_KEY or ""
        self.model = model or settings.LLM_MODEL
        self.timeout = timeout or settings.LLM_TIMEOUT_SECONDS

        # Infer base URL if not explicitly given
        if base_url:
            self.base_url = base_url.rstrip("/")
        elif settings.LLM_PROVIDER.lower() == "groq":
            self.base_url = "https://api.groq.com/openai/v1"
        else:
            self.base_url = "https://api.openai.com/v1"

    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> LLMResponse:
        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()
                tokens = data.get("usage", {}).get("total_tokens", 0)
                return LLMResponse(content=content, raw=data, tokens_used=tokens)
        except Exception as e:
            logger.error("OpenAI-compatible LLM request failed: %s", str(e))
            raise RuntimeError(f"LLM provider error: {str(e)}") from e


def get_llm_provider() -> BaseLLMProvider:
    """
    Factory function providing the configured LLM provider instance.
    """
    provider_type = (settings.LLM_PROVIDER or "mock").lower()

    if provider_type in ["openai", "groq", "custom"]:
        return OpenAICompatibleProvider(
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL,
            base_url=settings.LLM_BASE_URL,
            timeout=settings.LLM_TIMEOUT_SECONDS,
        )
    return MockLLMProvider()
