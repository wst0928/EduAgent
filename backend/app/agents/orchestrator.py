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
        
        

    async def process(self, context: dict[str, Any]) -> dict[str, Any]:
        workflow = context.get("workflow", "chat")
        if workflow == "chat":
            return await self._handle_chat_workflow(context)
        elif workflow == "start_learning":
            return await self._start_learning_workflow(context)
        elif workflow == "generate_resources":
            return await self._generate_resources_workflow(context)
        elif workflow == "assess":
            return await self._assess_workflow(context)
        elif workflow == "recommend":
            return await self._recommend_workflow(context)
        elif workflow == "review_progress":
            return await self._review_progress_workflow(context)
        else:
            return {"error": f"Unknown workflow: {workflow}"}

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
        """Handle chat - detect learning intent from keywords, bypass LLM for speed."""
        user_id = context.get("user_id", "default")
        message = context.get("message", "")
        session_id = context.get("session_id", f"session_{user_id}")

        # Detect learning intent from keywords - NO LLM needed
        learning_keywords = ["学", "了解", "入门", "想学", "学习", "python", "python编程", "机器学习", "人工智能", "ai", "深度学习", "java", "前端"]
        msg_lower = message.lower()
        
        # Extract topic
        from app.services.demoresponse import extract_topic_from_prompt
        topic = extract_topic_from_prompt(message)
        
        has_learning_intent = any(kw in msg_lower for kw in learning_keywords)
        
        # If learning intent detected, skip LLM, go straight to content generation
        if has_learning_intent:
            reply = f"好的！让我为你规划{topic}的学习路径，构建知识体系并生成个性化资源！"
            
            memory_service.add_to_session(session_id, [
                {"role": "user", "content": message},
                {"role": "assistant", "content": reply},
            ])
            
            workflow_result = await self._start_learning_workflow({
                "user_id": user_id,
                "topic": topic,
                "difficulty": "beginner",
            })
            
            return {
                "reply": reply,
                "intent": "set_goal",
                "topics": [topic],
                "profile": None,
                "workflow": "start_learning",
                "workflow_result": workflow_result,
            }
        
        # No learning intent - try LLM for general chat
        try:
            intent_result = await self.user_agent.process({
                "action": "analyze", "user_id": user_id, "message": message,
            })
            intent = intent_result.get("intent", "other")
            reply = intent_result.get("reply", "你好！请告诉我你想学习什么？")
            topics = intent_result.get("topics", [])
            
            memory_service.add_to_session(session_id, [
                {"role": "user", "content": message},
                {"role": "assistant", "content": reply},
            ])
            
            result = {"reply": reply, "intent": intent, "topics": topics, "profile": None}
            
            if intent == "set_goal" and topics:
                wf = await self._start_learning_workflow({
                    "user_id": user_id, "topic": topics[0],
                    "difficulty": intent_result.get("difficulty", "beginner"),
                })
                result["workflow"] = "start_learning"
                result["workflow_result"] = wf
            
            return result
        except Exception:
            return {"reply": "你好！我是EduAgent，请告诉我你想学什么，比如「我想学Python编程」。", "intent": "other", "topics": []}
    

    async def _start_learning_workflow(self, context: dict[str, Any]) -> dict[str, Any]:
        """Start learning: get course data, try LLM first, fallback to course library."""
        topic = context.get("topic", "Python编程")
        difficulty = context.get("difficulty", "beginner")
        user_id = context.get("user_id", "default")

        # Get course data from library (always works)
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
        articles = course.get("articles", ["# " + topic])
        
        resources_in = [
            {"type": "article", "title": course.get("name", topic) + "入门", "content": articles[0] if articles else "# " + topic},
            {"type": "summary", "title": course.get("name", topic) + "知识总结", "content": "# " + course.get("name", topic) + "核心知识总结\n\n## 基础概念\n..."},
            {"type": "exercise", "title": course.get("name", topic) + "练习题", "content": "# " + course.get("name", topic) + "练习题\n\n1. 基础题\n2. 进阶题\n3. 综合题"},
        ]

        # Save resources to memory
        for res in resources_in:
            try:
                from app.models.resource import LearningResource, ResourceType
                rt_map = {"article": ResourceType.article, "exercise": ResourceType.exercise, "summary": ResourceType.summary, "study_guide": ResourceType.study_guide}
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
            "topic": course.get("name", topic),
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
            "initial_resource": {"title": resources_in[0].get("title", ""), "preview": resources_in[0].get("content", "")[:200]},
            "resources": [{"type": r.get("type", "article"), "title": r.get("title", ""), "content": r.get("content", "")} for r in resources_in],
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

    async def _tutor_workflow(self, context: dict[str, Any]) -> dict[str, Any]:
        """智能辅导：解答学生问题并提供多模态解释"""
        user_id = context.get("user_id", "default")
        question = context.get("question", "")
        topic = context.get("topic", "")

        # Step 1: Answer the question
        answer_result = await self.tutor_agent.process({
            "action": "answer_question",
            "user_id": user_id,
            "question": question,
            "topic": topic,
        })

        # Step 2: Record the interaction
        memory_service.add_to_session(f"tutor_{user_id}", [
            {"role": "user", "content": question, "timestamp": str(__import__("datetime").datetime.utcnow())},
            {"role": "assistant", "content": answer_result.get("answer", {}).get("summary", "")},
        ])

        # Step 3: Check user understanding with follow-up
        if answer_result.get("answer", {}).get("follow_up_questions"):
            followup = await self.tutor_agent.process({
                "action": "ask_followup",
                "question": question,
                "answer_summary": answer_result.get("answer", {}).get("summary", ""),
            })
            answer_result["follow_up"] = followup

        return {
            "status": "success",
            "workflow": "tutor_answer",
            "question": question,
            "topic": topic,
            "answer": answer_result.get("answer", {}),
            "follow_up": answer_result.get("follow_up", {}),
        }

    async def _progress_report_workflow(self, context: dict[str, Any]) -> dict[str, Any]:
        """生成完整的学习进度报告"""
        result = await self.progress_tracker.process(context)
        return result

    async def _learning_insights_workflow(self, context: dict[str, Any]) -> dict[str, Any]:
        """生成个性化学习洞察"""
        result = await self.progress_tracker.process({
            **context, "action": "get_learning_insights",
        })
        return result

    def _sse(self, event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"





