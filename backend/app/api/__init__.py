"""Pydantic schemas for API request/response validation."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = "default"
    session_id: Optional[str] = None
    message: str
    workflow: str = "chat"


class ChatResponse(BaseModel):
    reply: str = ""
    workflow: Optional[str] = None
    workflow_result: Optional[dict[str, Any]] = None


class StartLearningRequest(BaseModel):
    user_id: str = "default"
    topic: str
    difficulty: str = "beginner"
    time_constraint: Optional[str] = None


class GenerateResourceRequest(BaseModel):
    user_id: str = "default"
    topic: str
    resource_type: str = "article"
    difficulty: int = 1
    resource_types: Optional[list[str]] = None


class QuizRequest(BaseModel):
    user_id: str = "default"
    topic: str
    difficulty: str = "beginner"
    num_questions: int = 5


class EvaluateRequest(BaseModel):
    quiz_id: str
    answers: list[int]


class FlashcardRequest(BaseModel):
    user_id: str = "default"
    topic: str
    num_cards: int = 10


class FeedbackRequest(BaseModel):
    resource_id: str
    feedback: str


class UserProfileResponse(BaseModel):
    user_id: str
    profile: dict[str, Any]
    goals: list[dict[str, Any]]
    learning_progress: dict[str, float]
