"""REST API routes - adds SSE streaming, recommendation, and progress endpoints."""
from __future__ import annotations

import json
from typing import Any, AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.agents.orchestrator import Orchestrator
from app.services.memory_service import memory_service

router = APIRouter(prefix="/api/v1", tags=["EduAgent"])

orchestrator = Orchestrator()
# ---- Chat & Streaming ----

@router.post("/chat")
async def chat(body: dict[str, Any]) -> dict[str, Any]:
    """Chat endpoint - direct keyword detection."""
    try:
        from app.services.demoresponse import extract_topic_from_prompt, get_course_data
        from app.models.resource import LearningResource, ResourceType
        from app.services.memory_service import memory_service
        msg = body.get("message", "")
        topic = extract_topic_from_prompt(msg)
        with open("D:/New project/routes_debug.log","a",encoding="utf-8") as f: f.write("TOPIC: " + repr(topic) + " MSG: " + msg + "\n")
        if not topic:
            return {"reply": "你好！我是 EduAgent，个性化学习助手。你可以告诉我你想学什么，比如「我想学Python」或「想了解机器学习」。", "intent": "other", "topics": []}
        c = get_course_data(topic)
        nm = c.get("name", topic)
        arts = c.get("articles", [])
        title_check = nm + "入门教程"
        existing = [r for r in memory_service.list_resources() if r.title == title_check]
        if arts and not existing:
            lr = LearningResource(title=title_check, resource_type=ResourceType.article, content=arts[0])
            memory_service.save_resource(lr)
        return {"reply": "好的！让我为你规划" + nm + "的学习路径！", "intent": "set_goal", "topics": [topic], "workflow": "start_learning", "workflow_result": {"status": "success", "topic": nm, "knowledge_graph": {"nodes": c.get("nodes", []), "edges": c.get("edges", [])}, "learning_path": {"title": nm + "学习路径", "overview": c.get("overview", ""), "milestones": c.get("milestones", []), "estimated_hours": c.get("total_hours", 10), "learning_tips": c.get("tips", []), "recommended_materials": c.get("materials", [])}, "resources": []}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(body: dict[str, Any]):
    """SSE streaming chat endpoint."""
    async def event_stream() -> AsyncGenerator[bytes, None]:
        async for sse_msg in orchestrator.process_stream({
            "workflow": "chat",
            "user_id": body.get("user_id", "default"),
            "message": body.get("message", ""),
        }):
            yield sse_msg.encode("utf-8")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---- Learning ----

@router.post("/learning/start")
async def start_learning(body: dict[str, Any]) -> dict[str, Any]:
    """Start a new learning journey."""
    try:
        result = await orchestrator.process({
            "workflow": "start_learning",
            "user_id": body.get("user_id", "default"),
            "topic": body.get("topic", ""),
            "difficulty": body.get("difficulty", "beginner"),
            "time_constraint": body.get("time_constraint", ""),
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Resources ----

@router.post("/resources/generate")
async def generate_resources(body: dict[str, Any]) -> dict[str, Any]:
    """Generate learning resources."""
    try:
        resource_types = body.get("resource_types", ["article"])
        result = await orchestrator.process({
            "workflow": "generate_resources",
            "user_id": body.get("user_id", "default"),
            "topic": body.get("topic", ""),
            "difficulty": body.get("difficulty", 1),
            "resource_types": resource_types,
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resources/regenerate")
async def regenerate_resource(body: dict[str, Any]) -> dict[str, Any]:
    """Regenerate based on feedback."""
    try:
        result = await orchestrator.resource_agent.process({
            "action": "regenerate",
            "resource_id": body.get("resource_id", ""),
            "feedback": body.get("feedback", ""),
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources")
async def list_resources(topic: str = "") -> dict[str, Any]:
    """List resources, optionally filtered by topic."""
    if topic:
        t_lower = topic.lower()
        resources = [r for r in memory_service.list_resources() if t_lower in r.title.lower()]
    else:
        resources = memory_service.list_resources()
    return {"resources": [r.model_dump() for r in resources], "count": len(resources)}


@router.get("/resources/by-topic/{topic}")
async def list_resources_by_topic(topic: str) -> dict:
    """List resources for a specific topic."""
    from app.services.memory_service import memory_service
    t_lower = topic.lower()
    resources = [r.model_dump() for r in memory_service.list_resources() 
                 if t_lower in r.title.lower()]
    return {"resources": resources, "count": len(resources)}

@router.get("/resources/{resource_id}")
async def get_resource(resource_id: str) -> dict[str, Any]:
    """Get a specific resource."""
    resource = memory_service.get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="资源未找到")
    return {"resource": resource.model_dump()}


# ---- Recommendation ----

@router.get("/recommendations")
async def get_recommendations(
    user_id: str = "default",
    topic: str = "",
    top_k: int = 5,
) -> dict[str, Any]:
    """Get personalized resource recommendations based on user profile."""
    result = await orchestrator.process({
        "workflow": "recommend",
        "user_id": user_id,
        "topic": topic,
        "top_k": top_k,
    })
    return result


# ---- Quiz ----

@router.post("/quiz/generate")
async def generate_quiz(body: dict[str, Any]) -> dict[str, Any]:
    """Generate a quiz."""
    try:
        result = await orchestrator.process({
            "workflow": "assess",
            "action": "generate_quiz",
            "user_id": body.get("user_id", "default"),
            "topic": body.get("topic", ""),
            "difficulty": body.get("difficulty", "beginner"),
            "num_questions": body.get("num_questions", 5),
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quiz/evaluate")
async def evaluate_quiz(body: dict[str, Any]) -> dict[str, Any]:
    """Evaluate quiz answers."""
    try:
        result = await orchestrator.process({
            "workflow": "assess",
            "action": "evaluate",
            "quiz_id": body.get("quiz_id", ""),
            "answers": body.get("answers", []),
            "user_id": body.get("user_id", "default"),
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flashcards/generate")
async def generate_flashcards(body: dict[str, Any]) -> dict[str, Any]:
    """Generate flashcards."""
    try:
        result = await orchestrator.assessment_agent.process({
            "action": "generate_flashcards",
            "topic": body.get("topic", ""),
            "num_cards": body.get("num_cards", 10),
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- User / Profile ----

@router.get("/users/{user_id}")
async def get_user_profile(user_id: str) -> dict[str, Any]:
    """Get user profile with all 8+ dimensions."""
    user = memory_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    return {
        "user_id": user_id,
        "profile": user.profile.model_dump(),
        "goals": [g.model_dump() for g in user.goals],
        "learning_progress": user.learning_progress,
        "quiz_history": user.quiz_history[-10:],
    }


# ---- Seed / Course Data ----

@router.post("/seed/course")
async def seed_course(body: dict[str, Any]) -> dict[str, Any]:
    """Initialize a default course knowledge base."""
    from app.data.seed_course import seed_knowledge_graph
    kg = seed_knowledge_graph(body.get("course_name", "人工智能导论"))
    return {
        "status": "success",
        "course": kg.name,
        "node_count": len(kg.nodes),
        "edge_count": len(kg.edges),
    }


@router.post("/seed/course-resources")
async def seed_course_resources(body: dict[str, Any]) -> dict[str, Any]:
    """Pre-generate sample resources for a course."""
    from app.data.seed_course import seed_sample_resources
    count = seed_sample_resources(body.get("course_name", "人工智能导论"))
    return {"status": "success", "resources_created": count}


# ---- Health ----

@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "EduAgent"}

