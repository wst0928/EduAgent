"""User Agent: understands learner profile, goals, and preferences.
   Extracts 8+ dimension dynamic learner profile via natural conversation."""
from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseAgent
from app.models.user import CognitiveStyle, LearningGoal, LearningStyle, User
from app.services.memory_service import memory_service


PROMPT = """你是一位教育心理咨询师，负责全面了解学习者的背景和目标。
你的职责：
1. 通过自然对话收集学习者的个人信息，构建多维度画像
2. 画像维度包含：专业方向、年级、知识基础、学习风格、认知风格、
   偏好难度、兴趣领域、易错点/薄弱环节、学习节奏、学习动机
3. 从对话中提取结构化的用户画像信息，更新已有维度
4. 识别和明确学习者的学习目标
5. 保持友好、鼓励的语气，帮助学习者明确自己的需求
"""


class UserAgent(BaseAgent):
    """Analyzes user input to build learner profile and extract learning goals."""

    def __init__(self) -> None:
        super().__init__(
            name="UserAgent",
            description="了解学习者背景、偏好和目标画像",
            system_prompt=PROMPT,
        )

    async def process(self, context: dict[str, Any]) -> dict[str, Any]:
        action = context.get("action", "analyze")
        user_id = context.get("user_id", "default")
        message = context.get("message", "")

        user = memory_service.get_user(user_id)
        if not user:
            user = memory_service.create_user(user_id)

        if action == "analyze":
            return await self._analyze_user_intent(user, message)
        elif action == "extract_profile":
            return await self._extract_profile(user, message)
        elif action == "update_goal":
            return self._update_goal_from_message(user, message)
        else:
            return {"reply": "你好！我是你的学习助手，请告诉我你想学习什么？"}

    async def _analyze_user_intent(self, user: User, message: str) -> dict[str, Any]:
        result = await self._llm_structured([
            {"role": "user", "content": f"""分析以下用户消息，提取学习意图。

用户当前画像：
- 专业方向：{user.profile.major or '未知'}
- 年级：{user.profile.grade or '未知'}
- 已有知识：{', '.join(user.profile.existing_knowledge) or '暂无'}
- 学习风格：{user.profile.learning_style.value}
- 认知风格：{user.profile.cognitive_style.value}
- 偏好难度：{user.profile.preferred_difficulty.value}
- 兴趣：{', '.join(user.profile.interests) or '暂无'}
- 易错点：{', '.join(user.profile.error_prone_areas) or '暂无'}
- 学习节奏：{user.profile.learning_pace}
- 学习动机：{user.profile.motivation}

消息：{message}

请返回JSON格式：
{{
  "intent": "set_goal | ask_question | request_resource | update_profile | other",
  "topics": ["提取的主题列表"],
  "difficulty": "beginner | intermediate | advanced",
  "needs_clarification": true/false,
  "clarification_question": "如果需要澄清，此处填写追问",
  "reply": "对用户的友好回复"
}}"""
            }])
        return result

    async def _extract_profile(self, user: User, conversation: str) -> dict[str, Any]:
        """Extract comprehensive learner profile (8+ dimensions) from conversation."""
        from app.models.user import DifficultyLevel, LearningStyle, CognitiveStyle
        result = await self._llm_structured([
            {"role": "user", "content": "从以下对话中提取全面的学生画像信息（不少于8个维度）。\n\n对话历史：\n" + conversation + "\n\n返回JSON格式，不在对话中的信息留空，不要编造：\n{\n  \"name\": \"用户名称\",\n  \"major\": \"专业方向\",\n  \"grade\": \"年级\",\n  \"existing_knowledge\": [],\n  \"learning_style\": \"mixed\",\n  \"cognitive_style\": \"analytical\",\n  \"preferred_difficulty\": \"beginner\",\n  \"interests\": [],\n  \"error_prone_areas\": [],\n  \"learning_pace\": \"normal\",\n  \"motivation\": \"career\",\n  \"goals\": []\n}"}
        ])

        # Apply all extracted dimensions with proper enum conversion
        string_fields = {"name", "major", "grade", "learning_pace", "motivation"}
        enum_map = {
            "learning_style": (LearningStyle, "mixed"),
            "cognitive_style": (CognitiveStyle, "analytical"),
            "preferred_difficulty": (DifficultyLevel, "beginner"),
        }

        for field in string_fields:
            val = result.get(field)
            if val:
                setattr(user.profile, field, val)

        for field, (enum_cls, default_val) in enum_map.items():
            val = result.get(field)
            if val:
                try:
                    setattr(user.profile, field, enum_cls(val))
                except (ValueError, Exception):
                    try:
                        setattr(user.profile, field, enum_cls(default_val))
                    except Exception:
                        pass

        for list_field in ("existing_knowledge", "interests", "error_prone_areas"):
            vals = result.get(list_field, [])
            if vals:
                existing = getattr(user.profile, list_field)
                merged = list(set(existing + vals))
                setattr(user.profile, list_field, merged)

        for goal_data in result.get("goals", []):
            goal = LearningGoal(
                topic=goal_data.get("topic", ""),
                description=goal_data.get("description", ""),
            )
            if goal.topic and goal.topic not in [g.topic for g in user.goals]:
                user.goals.append(goal)

        memory_service.update_user(user)
        return {"profile": user.profile.model_dump(), "goals": [g.model_dump() for g in user.goals]}

    def _update_goal_from_message(self, user: User, message: str) -> dict[str, Any]:
        goal = LearningGoal(topic=message, description=message)
        if message not in [g.topic for g in user.goals]:
            user.goals.append(goal)
            memory_service.update_user(user)
        return {"goal": goal.model_dump(), "message": f"已添加学习目标：{message}"}
