"""LLM service with short timeout."""
from __future__ import annotations

import json
import logging
from typing import Any, AsyncGenerator, Optional

from openai import AsyncOpenAI, APIConnectionError, RateLimitError

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Unified service for LLM API calls with short timeout."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            timeout=15.0,
            max_retries=0,
        )
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens

    def _get_last_user_message(self, messages: list[dict]) -> str:
        for m in reversed(messages):
            if m["role"] == "user":
                return m["content"]
        return ""

    async def chat(
        self,
        messages: list[dict],
        system_prompt: str = "",
        response_format: Optional[dict] = None,
        temperature: Optional[float] = None,
    ) -> str:
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": full_messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": self.max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""

    async def chat_structured(
        self,
        messages: list[dict],
        system_prompt: str = "",
        temperature: Optional[float] = None,
    ) -> dict:
        raw = await self.chat(
            messages=messages,
            system_prompt=system_prompt,
            response_format={"type": "json_object"},
            temperature=temperature or 0.3,
        )
        return json.loads(raw)

    async def chat_stream(
        self,
        messages: list[dict],
        system_prompt: str = "",
        temperature: Optional[float] = None,
    ) -> AsyncGenerator[str, None]:
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
            timeout=15.0,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content

    async def generate_embedding(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding

    async def content_safety_check(self, text: str) -> dict[str, Any]:
        return {"has_issue": False, "issue_type": "none", "issue_description": "", "suggestion": ""}


llm_service = LLMService()
