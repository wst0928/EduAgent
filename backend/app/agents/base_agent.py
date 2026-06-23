"""Base agent class that all specialized agents inherit from."""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from app.config import settings
from app.services.llm_service import llm_service
from app.services.memory_service import memory_service
from app.services.demoresponse import fallback_structured, extract_topic_from_prompt

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base agent with shared LLM and memory access."""

    def __init__(self, name: str, description: str, system_prompt: str = "") -> None:
        self.name = name
        self.description = description
        self.system_prompt = system_prompt or f"You are {name}, a specialized learning agent. {description}"

    @abstractmethod
    async def process(self, context: dict[str, Any]) -> dict[str, Any]:
        """Process incoming context and return results."""

    async def _llm_chat(self, messages: list[dict], **kwargs: Any) -> str:
        """Convenience wrapper for LLM chat."""
        return await llm_service.chat(
            messages=messages,
            system_prompt=self.system_prompt,
            **kwargs,
        )

    async def _llm_structured(self, messages: list[dict], **kwargs: Any) -> dict:
        """Try LLM first; on failure, return fallback with correct topic."""
        try:
            return await llm_service.chat_structured(
                messages=messages,
                system_prompt=self.system_prompt,
                **kwargs,
            )
        except Exception as e:
            logger.warning(f"LLM structured call failed for {self.name}: {e}")
            # Extract topic from the last user message for correct fallback
            last_msg = ""
            for m in reversed(messages):
                if m["role"] == "user":
                    last_msg = m["content"]
                    break
            fallback = fallback_structured(last_msg)
            return fallback

    def _get_user(self, user_id: str):
        return memory_service.get_user(user_id)

    def _get_session(self, session_id: str) -> list[dict]:
        return memory_service.get_session(session_id)

    def _build_context_window(self, messages: list[dict], max_pairs: int = 10) -> list[dict]:
        if len(messages) <= max_pairs:
            return messages
        return messages[-max_pairs:]
