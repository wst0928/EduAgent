"""Learning Path Agent: generates personalized learning roadmaps."""
from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseAgent
from app.services.memory_service import memory_service


PROMPT = """你是一位学习路径规划专家，擅长为学习者设计科学高效的个性化学习路径。
你的职责：
1. 根据学习者的目标、现有知识水平和可用时间，设计最优学习路径
2. 合理安排学习顺序，确保前置知识先学
3. 将大目标分解为可管理的小里程碑
4. 推荐合适的学习资源和练习
5. 根据学习进度动态调整路径
"""


class LearningPathAgent(BaseAgent):
    """Plans and optimizes personalized learning paths."""

    def __init__(self) -> None:
        super().__init__(
            name="LearningPathAgent",
            description="规划个性化学习路径和里程碑",
            system_prompt=PROMPT,
        )

    async def process(self, context: dict[str, Any]) -> dict[str, Any]:
        action = context.get("action", "create_path")
        user_id = context.get("user_id", "default")

        if action == "create_path":
            return await self._create_learning_path(context)
        elif action == "adjust_path":
            return await self._adjust_path(context)
        elif action == "get_progress":
            return await self._get_progress(user_id)
        else:
            return {"error": f"Unknown action: {action}"}

    async def _create_learning_path(self, context: dict[str, Any]) -> dict[str, Any]:
        user = self._get_user(context.get("user_id", "default"))
        topic = context.get("topic", "")
        time_constraint = context.get("time_constraint", "")
        target_level = context.get("target_level", "intermediate")

        user_info = ""
        if user:
            user_info = f"""
学习者信息：
- 已有知识：{', '.join(user.profile.existing_knowledge) or "无"}
- 学习风格：{user.profile.learning_style.value}
- 可用时间：{time_constraint or "不限"}
- 目标水平：{target_level}
"""

        result = await self._llm_structured([
            {"role": "user",
             "content": f"""为学习者设计个性化学习路径。

学习主题：{topic}
{user_info}

返回JSON格式：
{{
  "title": "学习路径标题",
  "overview": "总体学习路径描述",
  "estimated_total_hours": 20,
  "milestones": [
    {{
      "order": 1,
      "name": "里程碑名称",
      "description": "该阶段学习内容",
      "estimated_hours": 5,
      "difficulty": "beginner/intermediate/advanced",
      "topics": ["知识点1", "知识点2"],
      "objectives": ["完成目标1", "完成目标2"],
      "recommended_resource_types": ["article", "exercise", "quiz"]
    }}
  ],
  "learning_tips": ["学习建议1", "学习建议2"],
  "recommended_materials": ["推荐资料1", "推荐资料2"]
}}"""
            }])

        if user:
            user.learning_progress[topic] = 0.0
            memory_service.update_user(user)

        return result

    async def _adjust_path(self, context: dict[str, Any]) -> dict[str, Any]:
        user_id = context.get("user_id", "default")
        topic = context.get("topic", "")
        progress = context.get("progress", 0.0)
        feedback = context.get("feedback", "")

        user = self._get_user(user_id)
        if user:
            user.learning_progress[topic] = progress
            memory_service.update_user(user)

        result = await self._llm_structured([
            {"role": "user",
             "content": f"""根据学习进度调整学习路径。

学习主题：{topic}
当前进度：{progress * 100:.0f}%
学习者反馈：{feedback}

请返回调整后的学习路径（JSON格式，同之前的结构），
重点标注需要加强或跳过哪些部分。"""}
        ])
        return result

    async def _get_progress(self, user_id: str) -> dict[str, Any]:
        user = self._get_user(user_id)
        if not user:
            return {"error": "用户未找到"}
        return {
            "user_id": user_id,
            "learning_progress": user.learning_progress,
            "profile": user.profile.model_dump(),
        }
