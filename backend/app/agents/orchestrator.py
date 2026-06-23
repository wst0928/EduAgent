"""Orchestrator: coordinates all agents for end-to-end learning workflows.
   Adds: streaming, recommendation, progress tracking."""
from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator

from app.agents.assessment_agent import AssessmentAgent


from app.agents.base_agent import BaseAgent
from app.agents.knowledge_graph_agent import KnowledgeGraphAgent
from app.agents.learning_path_agent import LearningPathAgent
from app.agents.resource_generation_agent import ResourceGenerationAgent
from app.agents.user_agent import UserAgent
from app.services.memory_service import memory_service


class Orchestrator(BaseAgent):
    """Central coordinator that routes requests to the right agent(s)
    and manages multi-step learning workflows."""

    def __init__(self) -> None:
        super().__init__(
            name="Orchestrator",
            description="多智能体协同调度中心",
            system_prompt="你是一位经验丰富的学习协调员，负责理解用户的整体需求并协调各个专业Agent协同工作。",
        )
        self.user_agent = UserAgent()
        self.kg_agent = KnowledgeGraphAgent()
        self.resource_agent = ResourceGenerationAgent()
        self.path_agent = LearningPathAgent()
        self.assessment_agent = AssessmentAgent()
        
        

    async def process(self, context):
        w = context.get("workflow", "chat")
        if w == "chat":
            return await self._chat_v3(context)
        elif w == "start_learning":
            return await self._learn_v3(context)
        elif w == "generate_resources":
            return await self._gen_res_v3(context)
        elif w == "assess":
            return await self._assess_v3(context)
        elif w == "recommend":
            from app.services.memory_service import memory_service
            recs = memory_service.recommend_resources(context.get("user_id", "default"), context.get("topic", ""), context.get("top_k", 5))
            return {"status": "success", "recommendations": [r.model_dump() for r in recs]}
        return {"error": "unknown"}

    async def _chat_v3(self, context):
        msg = context.get("message", "")
        open("D:/New project/debug_v3.log","a",encoding="utf-8").write("CHAT_V3:" + msg + "\n")
        from app.services.demoresponse import extract_topic_from_prompt, get_course_data
        topic = extract_topic_from_prompt(msg)
        if not topic:
            t2 = msg.lower()
            kws = ["学", "python", "机器", "ai", "java", "编程", "数据", "了解", "入门"]
            if not any(k in t2 for k in kws):
                return {"reply": "你好！我是 EduAgent，个性化学习助手。你可以告诉我你想学什么，比如「我想学Python」或「想了解机器学习」。", "intent": "other", "topics": []}
        from app.models.resource import LearningResource, ResourceType
        from app.services.memory_service import memory_service
        c = get_course_data(topic)
        nm = c.get("name", topic)
        arts = c.get("articles", [])
        title_check = nm + "入门教程"
        existing = [r for r in memory_service.list_resources() if r.title == title_check]
        if arts and not existing:
            lr = LearningResource(title=title_check, resource_type=ResourceType.article, content=arts[0])
            memory_service.save_resource(lr)
        return {"reply": "好的！让我为你规划" + nm + "的学习路径！", "intent": "set_goal", "topics": [topic], "workflow": "start_learning", "workflow_result": {"status": "success", "topic": nm, "knowledge_graph": {"nodes": c.get("nodes", []), "edges": c.get("edges", [])}, "learning_path": {"title": nm + "学习路径", "overview": c.get("overview", ""), "milestones": c.get("milestones", []), "estimated_hours": c.get("total_hours", 10), "learning_tips": c.get("tips", []), "recommended_materials": c.get("materials", [])}, "resources": []}}
    async def _learn_v3(self, context):
        t = context.get("topic", "python")
        from app.services.demoresponse import get_course_data, extract_topic_from_prompt
        c = get_course_data(extract_topic_from_prompt(t))
        return {"status": "success", "topic": c.get("name", t), "knowledge_graph": {"nodes": c.get("nodes", []), "edges": c.get("edges", [])}, "learning_path": {"title": c.get("name", t) + "学习路径", "overview": c.get("overview", ""), "milestones": c.get("milestones", []), "estimated_hours": c.get("total_hours", 10), "learning_tips": c.get("tips", []), "recommended_materials": c.get("materials", [])}, "resources": [{"type": "article", "title": c.get("name", t) + "入门教程", "content": c.get("articles", [""])[0]}] if c.get("articles") else []}

    async def _gen_res_v3(self, context):
        t = context.get("topic", "")
        rt = context.get("resource_types", ["article"])
        from app.services.demoresponse import get_course_data, extract_topic_from_prompt
        c = get_course_data(extract_topic_from_prompt(t))
        from app.models.resource import LearningResource, ResourceType
        from app.services.memory_service import memory_service
        out = []
        arts = c.get("articles", [])
        if arts and "article" in rt:
            lr = LearningResource(title=c.get("name", t)+"教程", resource_type=ResourceType.article, content=arts[0])
            memory_service.save_resource(lr)
            out.append(lr.model_dump())
        return {"status": "success", "count": len(out), "resources": out}

    async def _assess_v3(self, context):
        action = context.get("action", "generate_quiz")
        topic = context.get("topic", "")
        from app.services.demoresponse import get_course_data, extract_topic_from_prompt
        c = get_course_data(extract_topic_from_prompt(topic))
        questions = c.get("practice_questions", [])
        if not questions:
            questions = [{"question": topic+"的核心概念是？", "options": ["A. 概念1", "B. 概念2", "C. 概念3", "D. 概念4"], "correct_index": 0, "explanation": "这是核心概念"}]
        return {"resource_id": "quiz_"+topic, "quiz": {"title": topic+"测验", "questions": questions}}

    async def process_stream(
        self, context: dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """Process with SSE streaming output. Also triggers full workflow when needed."""
        workflow = context.get("workflow", "chat")
        user_id = context.get("user_id", "default")
        message = context.get("message", "")

        yield self._sse("status", {"phase": "analyzing", "label": "正在分析你的需求..."})

        # Step 1: Analyze user intent
        intent_result = await self.user_agent.process({
            "action": "analyze",
            "user_id": user_id,
            "message": message,
        })

        reply = intent_result.get("reply", "")
        intent = intent_result.get("intent", "other")
        topics = intent_result.get("topics", [])

        yield self._sse("stream", {"token": reply})

        # Step 2: If setting a learning goal, trigger full workflow
        if intent == "set_goal" and topics:
            yield self._sse("status", {"phase": "building_kg", "label": "正在构建知识图谱..."})
            yield self._sse("stream", {"token": "\n\n让我为你构建完整的知识体系和学习路径...\n\n"})

            topic = topics[0]
            difficulty = intent_result.get("difficulty", "beginner")

            workflow_result = await self._start_learning_workflow({
                "user_id": user_id,
                "topic": topic,
                "difficulty": difficulty,
            })

            yield self._sse("workflow", {
                "workflow": "start_learning",
                "workflow_result": workflow_result,
            })
            yield self._sse("status", {"phase": "complete", "label": "学习准备就绪！"})
        else:
            yield self._sse("status", {"phase": "complete", "label": "分析完成"})

        yield self._sse("done", {})

    async def _handle_chat_workflow(self, context: dict[str, Any]) -> dict[str, Any]:
        """Handle chat with pure keyword detection - no LLM call."""
        user_id = context.get("user_id", "default")
        message = context.get("message", "")
        session_id = context.get("session_id", f"session_{user_id}")

        from app.services.demoresponse import extract_topic_from_prompt
        
        msg_lower = message.lower()
        learning_keywords = ["学", "了解", "入门", "想学", "学习", "python", "机器", "人工智能", "ai", "深度", "java", "前端", "编程", "数据"]
        has_intent = any(kw in msg_lower for kw in learning_keywords)
        
        intent = "set_goal" if has_intent else "other"
        topic = extract_topic_from_prompt(message) if has_intent else ""
        
        if has_intent:
            reply = f"好的！让我为你规划{topic}的学习路径！"
        else:
            reply = "你好！我是你的学习助手，请告诉我你想学习什么。"

        memory_service.add_to_session(session_id, [
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply},
        ])

        result = {"reply": reply, "intent": intent, "topics": [topic] if topic else [], "profile": None}

        if intent == "set_goal" and topic:
            wf = await self._start_learning_workflow({
                "user_id": user_id, "topic": topic,
                "difficulty": "beginner",
            })
            result["workflow"] = "start_learning"
            result["workflow_result"] = wf

        return result
    async def _start_learning_workflow(self, context: dict[str, Any]) -> dict[str, Any]:
        """Start learning: instant from course library - no LLM."""
        topic = context.get("topic", "Python编程")
        difficulty = context.get("difficulty", "beginner")
        user_id = context.get("user_id", "default")

        from app.services.demoresponse import get_course_data, extract_topic_from_prompt
        course = get_course_data(extract_topic_from_prompt(topic))
        
        nodes = course.get("nodes", [])
        edges = course.get("edges", [])
        milestones = course.get("milestones", [])
        path_title = course.get("name", topic) + "学习路径"
        path_overview = course.get("overview", "")
        total_hours = course.get("total_hours", 10)
        tips = course.get("tips", [])
        materials = course.get("materials", [])
        course_name = course.get("name", topic)

        # Generate resources from course data
        resources_out = []
        articles = course.get("articles", [])
        if articles:
            resources_out.append({"type": "article", "title": course_name + "入门教程", "content": articles[0]})
        
        # Save to memory
        from app.models.resource import LearningResource, ResourceType
        for res in resources_out:
            try:
                rt_map = {"article": ResourceType.article, "exercise": ResourceType.exercise, "summary": ResourceType.summary}
                r = LearningResource(
                    title=res.get("title", ""),
                    resource_type=rt_map.get(res.get("type", "article"), ResourceType.article),
                    content=res.get("content", ""),
                    difficulty=1 if difficulty == "beginner" else 3,
                )
                memory_service.save_resource(r)
            except Exception:
                pass

        return {
            "status": "success",
            "topic": course_name,
            "difficulty": difficulty,
            "knowledge_graph": {"node_count": len(nodes), "edge_count": len(edges), "nodes": nodes, "edges": edges},
            "learning_path": {
                "title": path_title,
                "overview": path_overview,
                "milestones": milestones,
                "estimated_hours": total_hours,
                "learning_tips": tips,
                "recommended_materials": materials,
            },
            "resources": resources_out,
        }
    async def _generate_resources_workflow(self, context: dict[str, Any]) -> dict[str, Any]:
        tasks = []
        resource_types = context.get("resource_types",
                                      ["article", "summary", "exercise"])

        for res_type in resource_types:
            tasks.append(self.resource_agent.process({
                "action": "generate",
                "user_id": context.get("user_id", "default"),
                "topic": context.get("topic", ""),
                "resource_type": res_type,
                "difficulty": context.get("difficulty", 1),
            }))

        results = await asyncio.gather(*tasks)
        resources = [r.get("resource", {}) for r in results]

        return {
            "status": "success",
            "count": len(resources),
            "resources": resources,
        }

    async def _recommend_workflow(self, context: dict[str, Any]) -> dict[str, Any]:
        """Recommend resources based on user profile."""
        user_id = context.get("user_id", "default")
        topic = context.get("topic", "")
        top_k = context.get("top_k", 5)

        recommendations = memory_service.recommend_resources(
            user_id=user_id, topic=topic, top_k=top_k,
        )

        return {
            "status": "success",
            "recommendations": [r.model_dump() for r in recommendations],
            "count": len(recommendations),
        }

    async def _assess_workflow(self, context: dict[str, Any]) -> dict[str, Any]:
        action = context.get("action", "generate_quiz")
        if action == "generate_quiz":
            result = await self.assessment_agent.process(context)
            # Record quiz in user history
            user_id = context.get("user_id", "default")
            user = memory_service.get_user(user_id)
            if user:
                user.quiz_history.append({
                    "topic": context.get("topic", ""),
                    "quiz_id": result.get("resource_id", ""),
                    "timestamp": str(__import__("datetime").datetime.utcnow()),
                })
                memory_service.update_user(user)
            return result
        elif action == "evaluate":
            return await self.assessment_agent.process({
                **context, "action": "evaluate_answer",
            })
        else:
            return {"error": f"Unknown assessment action: {action}"}

    async def _review_progress_workflow(self, context: dict[str, Any]) -> dict[str, Any]:
        user_id = context.get("user_id", "default")
        topic = context.get("topic", "")

        progress = await self.path_agent.process({
            "action": "get_progress",
            "user_id": user_id,
        })

        # Get recommendations
        recommendations = memory_service.recommend_resources(
            user_id=user_id, topic=topic, top_k=3,
        )

        return {
            "status": "success",
            "progress": progress,
            "recommendations": [r.model_dump() for r in recommendations],
            "suggestions": "根据当前进度，建议继续按计划学习或调整难易度。",
        }

    def _sse(self, event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"






# FORCE_RECOMPILE v2

# VERSION: 2026-06-23T15:48:30.812824
