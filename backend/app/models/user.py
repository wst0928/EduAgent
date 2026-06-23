"""User models for learner profile and goals."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DifficultyLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class LearningStyle(str, Enum):
    visual = "visual"
    textual = "textual"
    interactive = "interactive"
    mixed = "mixed"


class CognitiveStyle(str, Enum):
    """认知风格维度"""
    analytical = "analytical"          # 分析型：喜欢拆解、逻辑推理
    holistic = "holistic"              # 整体型：喜欢全局视角、系统思维
    sequential = "sequential"          # 序列型：喜欢循序渐进、线性学习
    exploratory = "exploratory"        # 探索型：喜欢自由探索、项目驱动


class LearningGoal(BaseModel):
    id: str = Field(default_factory=lambda: f"goal_{datetime.utcnow().timestamp()}")
    topic: str
    description: str = ""
    target_level: DifficultyLevel = DifficultyLevel.intermediate
    time_constraint: Optional[str] = None
    priority: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserProfile(BaseModel):
    """8+ 维度动态学生画像"""
    name: str = ""
    major: str = ""                                  # 专业方向
    grade: str = ""                                  # 年级
    existing_knowledge: list[str] = Field(default_factory=list)    # 知识基础
    learning_style: LearningStyle = LearningStyle.mixed             # 学习风格（视觉/文本/交互/混合）
    cognitive_style: CognitiveStyle = CognitiveStyle.analytical     # 认知风格（分析/整体/序列/探索）
    preferred_difficulty: DifficultyLevel = DifficultyLevel.beginner # 偏好难度
    interests: list[str] = Field(default_factory=list)               # 兴趣领域
    error_prone_areas: list[str] = Field(default_factory=list)       # 易错点偏好/薄弱环节
    learning_pace: str = "normal"                      # 学习节奏（slow/normal/fast）
    motivation: str = "career"                         # 学习动机（career/academic/personal）


class User(BaseModel):
    id: str
    profile: UserProfile = Field(default_factory=UserProfile)
    goals: list[LearningGoal] = Field(default_factory=list)
    conversation_history: list[dict] = Field(default_factory=list)
    learning_progress: dict[str, float] = Field(default_factory=dict)
    quiz_history: list[dict] = Field(default_factory=list)       # 测验历史
    resource_feedback: list[dict] = Field(default_factory=list)   # 资源反馈历史
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
