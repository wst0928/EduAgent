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
    """Main chat endpoint - handles conversational learning interactions."""
    try:
        result = await orchestrator.process({
            "workflow": body.get("workflow", "chat"),
            "user_id": body.get("user_id", "default"),
            "session_id": body.get("session_id"),
            "message": body.get("message", ""),
        })
        return result
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
async def list_resources() -> dict[str, Any]:
    """List all resources."""
    resources = memory_service.list_resources()
    return {"resources": [r.model_dump() for r in resources], "count": len(resources)}


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


# ---- Progress ----

@router.get("/progress/{user_id}")
async def get_progress(user_id: str, topic: str = "") -> dict[str, Any]:
    """Get learner progress with recommendations."""
    result = await orchestrator.process({
        "workflow": "review_progress",
        "user_id": user_id,
        "topic": topic,
    })
    return result


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


# ---- Tutor (智能辅导) ----

@router.post("/tutor/ask")
async def tutor_ask(body: dict[str, Any]) -> dict[str, Any]:
    """Ask a question to the AI tutor for intelligent tutoring."""
    try:
        result = await orchestrator.process({
            "workflow": "tutor",
            "user_id": body.get("user_id", "default"),
            "question": body.get("question", ""),
            "topic": body.get("topic", ""),
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Progress (学习效果追踪) ----

@router.get("/progress/report/{user_id}")
async def get_progress_report(
    user_id: str = "default",
    topic: str = "",
) -> dict[str, Any]:
    """Get comprehensive learning progress report."""
    try:
        result = await orchestrator.process({
            "workflow": "progress_report",
            "action": "get_progress_report",
            "user_id": user_id,
            "topic": topic,
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/{user_id}")
async def get_learning_insights(user_id: str = "default") -> dict[str, Any]:
    """Get personalized learning insights and recommendations."""
    try:
        result = await orchestrator.process({
            "workflow": "learning_insights",
            "user_id": user_id,
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/progress/adapt-plan")
async def adapt_learning_plan(body: dict[str, Any]) -> dict[str, Any]:
    """Dynamically adjust learning plan based on progress."""
    try:
        result = await orchestrator.process({
            "workflow": "progress_report",
            "action": "adapt_learning_plan",
            "user_id": body.get("user_id", "default"),
            "current_plan": body.get("current_plan", {}),
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Health ----

@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "EduAgent"}

