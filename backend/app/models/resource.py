"""Learning resource models for generated content."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ResourceType(str, Enum):
    article = "article"
    summary = "summary"
    quiz = "quiz"
    exercise = "exercise"
    code_example = "code_example"
    mind_map = "mind_map"
    study_guide = "study_guide"
    flashcard = "flashcard"


class ResourceDifficulty(int, Enum):
    beginner = 1
    easy = 2
    intermediate = 3
    hard = 4
    advanced = 5


class ResourceMetadata(BaseModel):
    estimated_read_time_minutes: int = 5
    related_concepts: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    source: str = "ai_generated"
    language: str = "zh-CN"


class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correct_index: int
    explanation: str = ""
    difficulty: int = 1


class QuizContent(BaseModel):
    title: str
    questions: list[QuizQuestion]
    passing_score: int = 60


class FlashcardContent(BaseModel):
    cards: list[dict[str, str]]


class LearningResource(BaseModel):
    id: str = Field(default_factory=lambda: f"res_{datetime.utcnow().timestamp()}")
    title: str
    resource_type: ResourceType
    content: str = ""
    difficulty: ResourceDifficulty = ResourceDifficulty.beginner
    metadata: ResourceMetadata = Field(default_factory=ResourceMetadata)
    knowledge_node_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    quiz_content: Optional[QuizContent] = None
    flashcard_content: Optional[FlashcardContent] = None
    feedback_score: float = 0.0
    feedback_count: int = 0
