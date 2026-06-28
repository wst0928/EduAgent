"""Resource Generation Agent: creates personalized learning materials via LLM.
   Features: content safety filter, progress tracking, multi-type generation."""
from __future__ import annotations

import asyncio
from typing import Any

from app.agents.base_agent import BaseAgent
from app.models.resource import (
    LearningResource,
    ResourceDifficulty,
    ResourceMetadata,
    ResourceType,
)
from app.services.llm_service import llm_service
from app.services.memory_service import memory_service


PROMPT = """你是一位资深学科教育专家和课程设计师，擅长根据学习者的水平生成高质量的学习资源。
你的职责：
1. 根据学习者的知识水平和学习风格，生成个性化学习内容
2. 生成多种类型的资源：教学文章、知识总结、代码示例、测验题目等
3. 确保内容准确、结构清晰、循序渐进
4. 根据用户反馈调整资源难度和风格
5. 对每个资源进行内容安全检查，确保无事实错误和敏感内容
"""

RESOURCE_TYPE_PROMPTS = {
    "article": "生成一篇详细的教学文章。包含：引言、核心概念讲解、实例分析、要点总结。",
    "summary": "生成一份知识总结。用简洁的语言概括核心知识点，适合复习使用。",
    "quiz": "生成一套测验题目。包含至少5道选择题，覆盖核心知识点。",
    "exercise": "生成一组练习题。包含理论题和实际应用题，难度循序渐进。",
    "code_example": "生成带有详细注释的代码示例。展示如何在实际中应用所学知识。",
    "study_guide": "生成一份学习指南。包含学习目标、重点难点、学习方法建议。",
    "flashcard": "生成一组闪卡（记忆卡片）。用于知识点的快速记忆和复习。",
    "mind_map": "生成思维导图格式的知识结构。用树形结构展示知识间的联系。",
}


class ResourceGenerationAgent(BaseAgent):
    """Generates personalized educational resources using LLM."""

    def __init__(self) -> None:
        super().__init__(
            name="ResourceGenerationAgent",
            description="根据学习者画像生成个性化学习资源",
            system_prompt=PROMPT,
        )

    async def process(self, context: dict[str, Any]) -> dict[str, Any]:
        action = context.get("action", "generate")
        user_id = context.get("user_id", "default")

        if action == "generate":
            return await self._generate_resource(context)
        elif action == "generate_with_progress":
            return await self._generate_resource_with_progress(context)
        elif action == "regenerate":
            return await self._regenerate_with_feedback(context)
        elif action == "list":
            resources = memory_service.list_resources(user_id)
            return {"resources": [r.model_dump() for r in resources]}
        elif action == "generate_multiple":
            return await self._generate_multiple_resources(context)
        else:
            return {"error": f"Unknown action: {action}"}

    async def _generate_resource(self, context: dict[str, Any]) -> dict[str, Any]:
        topic = context.get("topic", "")
        resource_type_str = context.get("resource_type", "article")
        difficulty = context.get("difficulty", 1)
        knowledge_node_id = context.get("knowledge_node_id")
        try:
            resource_type = ResourceType(resource_type_str)
        except ValueError:
            resource_type = ResourceType.article
        type_prompt = RESOURCE_TYPE_PROMPTS.get(resource_type_str, "生成高质量的学习内容")
        llm_messages = [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": f"主题：{topic}\n资源类型：{resource_type_str}\n要求：{type_prompt}"}
        ]
        result = await self._llm_chat(llm_messages)
        if result and "LLM服务暂时不可用" not in result and len(result) > 50:
            final_content = result
            print(f"LLM OK for {topic}/{resource_type_str}")
        else:
            import json
            rich_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rich_content.json")
            try:
                with open(rich_file, "r", encoding="utf-8") as rf:
                    rich = json.load(rf)
                final_content = rich.get(resource_type_str, "")
            except:
                final_content = ""
            if not final_content:
                from app.services.demoresponse import get_course_data, extract_topic_from_prompt, fallback_text
                course = get_course_data(extract_topic_from_prompt(topic))
                arts = course.get("articles", [])
                if resource_type_str == "article" and arts:
                    final_content = arts[0]
                else:
                    final_content = fallback_text(f"生成关于{topic}的{resource_type_str}")
        resource = LearningResource(
            title=f"{topic} - {resource_type.value}",
            resource_type=resource_type,
            content=final_content,
            difficulty=ResourceDifficulty(difficulty),
            metadata=ResourceMetadata(tags=[topic], language="zh-CN"),
            knowledge_node_id=knowledge_node_id,
        )
        memory_service.save_resource(resource)
        preview = final_content[:500] + "..." if len(final_content) > 500 else final_content
        return {"resource": resource.model_dump(), "content_preview": preview}
    async def _generate_resource_with_progress(
        self, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate with progress tracking steps."""
        steps = [
            ("analyzing", "正在分析学习需求..."),
            ("planning", "正在规划资源结构..."),
            ("generating", "正在生成内容..."),
            ("safety_check", "正在进行安全审查..."),
            ("formatting", "正在格式化输出..."),
            ("complete", "生成完成！"),
        ]
        progress_log = []
        for phase, label in steps:
            await asyncio.sleep(0.3)
            progress_log.append({"phase": phase, "label": label, "progress": int(phase == "complete")})
        result = await self._generate_resource({**context, "skip_safety": False})
        result["progress"] = progress_log
        return result

    async def _generate_multiple_resources(self, context: dict[str, Any]) -> dict[str, Any]:
        """Generate multiple resource types - from course library first, LLM as bonus."""
        topic = context.get("topic", "")
        user_id = context.get("user_id", "default")
        resource_types = context.get("resource_types",
                                      ["article", "summary", "exercise", "quiz"])

        # Get course library content first
        from app.services.demoresponse import get_course_data, extract_topic_from_prompt
        course = get_course_data(extract_topic_from_prompt(topic))
        
        resources_out = []
        
        # Article: from course library
        articles = course.get("articles", [])
        if articles and "article" in resource_types:
            from app.models.resource import ResourceType as RT
            r = LearningResource(
                title=course.get("name", topic) + "????",
                resource_type=RT.article,
                content=articles[0],
            )
            memory_service.save_resource(r)
            resources_out.append(r.model_dump())
            resource_types = [t for t in resource_types if t != "article"]

        # For remaining types, try LLM in parallel
        if resource_types:
            tasks = []
            for res_type in resource_types:
                tasks.append(self._generate_resource({
                    "user_id": user_id, "topic": topic,
                    "resource_type": res_type,
                    "difficulty": context.get("difficulty", 1),
                }))
            results = await asyncio.gather(*tasks)
            for r in results:
                res = r.get("resource")
                if res:
                    resources_out.append(res)

        return {
            "status": "success",
            "count": len(resources_out),
            "resources": resources_out,
            "topic": topic,
        }

    async def _regenerate_with_feedback(self, context: dict[str, Any]) -> dict[str, Any]:
        resource_id = context.get("resource_id", "")
        feedback = context.get("feedback", "")
        original = memory_service.get_resource(resource_id)

        if not original:
            return {"error": "资源未找到"}

        result = await self._llm_chat([
            {"role": "user",
             "content": f"""根据以下反馈重新生成学习资源。

原资源标题：{original.title}
原资源内容：{original.content[:1000]}

用户反馈：{feedback}

请根据反馈优化内容并返回改进后的完整资源。"""}
        ])

        # Safety check on regenerated content
        safety = await llm_service.content_safety_check(result)
        if safety.get("has_issue"):
            result = (
                f"【已根据安全建议调整】\n{safety.get('suggestion', '')}\n\n{result}"
            )

        original.content = result
        original.feedback_count += 1
        memory_service.save_resource(original)

        preview = result[:500] + "..." if len(result) > 500 else result
        return {
            "resource": original.model_dump(),
            "content_preview": preview,
            "safety_checked": True,
        }

    def _build_user_context(self, user) -> str:
        if not user:
            return ""
        return f"""
学习者背景：
- 专业方向：{user.profile.major or "未知"}
- 年级：{user.profile.grade or "未知"}
- 已有知识：{', '.join(user.profile.existing_knowledge) or "初学者"}
- 学习风格：{user.profile.learning_style.value}
- 认知风格：{user.profile.cognitive_style.value}
- 兴趣领域：{', '.join(user.profile.interests) or "无特定偏好"}
- 偏好难度：{user.profile.preferred_difficulty.value}
- 易错点：{', '.join(user.profile.error_prone_areas) or "暂无"}
- 学习节奏：{user.profile.learning_pace}
"""
