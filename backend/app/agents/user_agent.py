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
        """Pure keyword-based intent analysis - no LLM."""
        msg_lower = message.lower()

        learning_kw = ["学", "了解", "入门", "想学", "学习", "python", "机器", "人工智能", "ai", "深度", "java", "前端", "编程", "数据", "算法", "网络", "sql", "html", "css", "js", "javascript", "c++", "c语言", "go语言", "rust"]
        quiz_kw = ["测验", "测试", "题目", "练习", "考试", "quiz", "做题"]

        has_learning_intent = any(k in msg_lower for k in learning_kw)
        has_quiz_intent = any(k in msg_lower for k in quiz_kw)

        from app.services.demoresponse import extract_topic_from_prompt
        topic = extract_topic_from_prompt(message)

        intent = "set_goal" if has_learning_intent else ("assess" if has_quiz_intent else "other")
        tname = topic if topic and topic != "Python" else "Python编程"

        if intent == "set_goal":
            reply = f"好的！让我为你规划{tname}的学习路径！" if topic else "好的，请告诉我你想学习什么具体的课程？"
        elif intent == "assess":
            reply = f"让我为你生成{tname}的测验题！" if topic else "你想要测试哪个课程？"
        else:
            reply = "你好！我是你的学习助手。请告诉我你想学习什么？"

        return {
            "intent": intent,
            "topics": [tname] if has_learning_intent else [],
            "difficulty": "beginner",
            "needs_clarification": False,
            "clarification_question": "",
            "reply": reply,
        }
    def _update_goal_from_message(self, user: User, message: str) -> dict[str, Any]:
        goal = LearningGoal(topic=message, description=message)
        if message not in [g.topic for g in user.goals]:
            user.goals.append(goal)
            memory_service.update_user(user)
        return {"goal": goal.model_dump(), "message": f"已添加学习目标：{message}"}
