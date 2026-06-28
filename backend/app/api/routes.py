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
_quiz_store: dict[str, dict] = {}


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
    return resource.model_dump()
@router.post("/quiz/generate")
async def generate_quiz(body: dict) -> dict:
    topic = body.get("topic", "Python编程")
    from app.services.demoresponse import extract_topic_from_prompt, get_course_data
    course = get_course_data(extract_topic_from_prompt(topic))
    nm = course.get("name", topic)
    quiz_id = "q_" + str(__import__("time").time()).replace(".", "")
    
    # Try assessment agent (DeepSeek) first
    qs = []
    try:
        agent_result = await orchestrator.assessment_agent._generate_quiz({"topic": topic, "difficulty": "beginner", "num_questions": 5})
        if agent_result and agent_result.get("quiz"):
            quiz_data = agent_result["quiz"]
            qs = quiz_data.get("questions", [])
    except:
        pass
    
    # Fallback: topic-specific questions
    if not qs:
        qs = []
        course_key = extract_topic_from_prompt(topic)
        if "python" in course_key or "python" in topic.lower():
            qs = [
                {"question": "Python中`len([1,2,3])`的值是？", "options": ["2", "3", "4", "报错"], "correct_index": 1, "explanation": "len()返回列表元素个数"},
                {"question": "定义函数的正确关键字是？", "options": ["function", "def", "define", "func"], "correct_index": 1, "explanation": "Python使用def关键字"},
                {"question": "列表推导式`[x*2 for x in range(3)]`的结果？", "options": ["[0,2,4]", "[0,2,6]", "[1,2,3]", "[2,4,6]"], "correct_index": 0, "explanation": "x取0,1,2"},
                {"question": "以下哪个是合法的变量名？", "options": ["2name", "my_name", "my-name", "class"], "correct_index": 1, "explanation": "变量名不能以数字开头"},
                {"question": "try语句的作用是？", "options": ["定义函数", "处理异常", "创建循环", "导入模块"], "correct_index": 1, "explanation": "try/except用于异常处理"},
            ]
        elif "机器" in topic or "machine" in course_key or "ml" in course_key:
            qs = [
                {"question": "以下哪个是监督学习的典型任务？", "options": ["聚类", "分类", "降维", "密度估计"], "correct_index": 1, "explanation": "分类是监督学习的典型任务"}, 
                {"question": "K-Means算法属于哪种学习范式？", "options": ["监督学习", "无监督学习", "强化学习", "半监督学习"], "correct_index": 1, "explanation": "K-Means是无监督聚类算法"}, 
                {"question": "以下哪个是防止过拟合的常用方法？", "options": ["增加模型层数", "正则化", "增加学习率", "减少训练数据"], "correct_index": 1, "explanation": "正则化是常用的防止过拟合方法"}, 
                {"question": "决策树中信息增益越大表示什么？", "options": ["纯度越低", "纯度越高", "分支越多", "深度越大"], "correct_index": 1, "explanation": "信息增益越大表示纯度提升越多"}, 
                {"question": "交叉验证的主要目的是？", "options": ["提高训练速度", "评估模型泛化能力", "减少内存占用", "增加模型复杂度"], "correct_index": 1, "explanation": "交叉验证用于评估模型的泛化能力"}, 
            ]
        elif "人工智能" in topic or "ai" in course_key:
            qs = [
                {"question": "图灵测试是用来测试什么的？", "options": ["计算机运算速度", "机器智能水平", "程序正确性", "网络性能"], "correct_index": 1, "explanation": "图灵测试用于判断机器是否具有智能"}, 
                {"question": "A*搜索算法中，h(n)代表什么？", "options": ["实际代价", "启发式估计", "搜索深度", "节点数量"], "correct_index": 1, "explanation": "h(n)是从当前节点到目标节点的启发式估计代价"}, 
                {"question": "反向传播算法主要用于训练哪种模型？", "options": ["决策树", "神经网络", "SVM", "K-means"], "correct_index": 1, "explanation": "反向传播是训练神经网络的核心算法"}, 
                {"question": "Transformer架构的核心创新是什么？", "options": ["卷积操作", "循环结构", "自注意力机制", "门控单元"], "correct_index": 2, "explanation": "自注意力机制是Transformer的核心创新"}, 
                {"question": "以下哪个是AI伦理关注的问题？", "options": ["算法效率", "数据隐私", "编程语言选择", "硬件配置"], "correct_index": 1, "explanation": "数据隐私是AI伦理的重要关注点"}, 
            ]
        else:
            qs = [
                {"question": f"{nm}的核心概念是什么？", "options": ["概念A", "概念B", "概念C", "概念D"], "correct_index": 0, "explanation": "这是核心概念"}, 
                {"question": f"学习{nm}需要什么前置知识？", "options": ["不需要", "数学基础", "编程基础", "英语基础"], "correct_index": 2, "explanation": "编程基础是必要前提"}, 
                {"question": f"{nm}的主要应用领域是？", "options": ["领域A", "领域B", "领域C", "领域D"], "correct_index": 0, "explanation": "这是主要应用领域"}, 
            ]
    
    from app.models.resource import QuizContent, QuizQuestion, LearningResource, ResourceType
    quiz_content = QuizContent(title=nm + " 测验", questions=[QuizQuestion(**q) for q in qs])
    resource = LearningResource(title=nm + " - 测验评估", resource_type=ResourceType.quiz, quiz_content=quiz_content)
    resource.id = quiz_id
    from app.services.memory_service import memory_service
    memory_service.save_resource(resource)
    display_qs = [{"question": q["question"], "options": q["options"], "difficulty": 1} for q in qs]
    return {"resource_id": quiz_id, "quiz": {"title": nm + " 测验", "questions": display_qs}}
@router.post("/quiz/evaluate")
async def evaluate_quiz_v2(body: dict) -> dict:
    qid = body.get("quiz_id", "")
    answers = body.get("answers", [])
    from app.services.memory_service import memory_service
    resource = memory_service.get_resource(qid)
    if resource and resource.quiz_content:
        quiz = resource.quiz_content
        results = []
        correct_count = 0
        for i, (question, answer_idx) in enumerate(zip(quiz.questions, answers)):
            is_correct = answer_idx == question.correct_index
            if is_correct:
                correct_count += 1
            user_ans = question.options[answer_idx] if isinstance(answer_idx, int) and answer_idx < len(question.options) else "未作答"
            results.append({"question_num": i+1, "question": question.question, "user_answer": user_ans, "correct_answer": question.options[question.correct_index], "is_correct": is_correct, "explanation": question.explanation})
        total = len(quiz.questions)
        score = int(correct_count / total * 100) if total > 0 else 0
        return {"score": score, "correct": correct_count, "total": total, "passed": score >= 60, "results": results, "feedback": ""}
    fb_qs = [
        {"q": "Python中`len([1,2,3])`的值是？", "op": ["2", "3", "4", "报错"], "ci": 1, "ex": "len()返回列表元素个数"},
        {"q": "定义函数的正确关键字是？", "op": ["function", "def", "define", "func"], "ci": 1, "ex": "Python使用def关键字"},
        {"q": "列表推导式`[x*2 for x in range(3)]`的结果？", "op": ["[0,2,4]", "[0,2,6]", "[1,2,3]", "[2,4,6]"], "ci": 0, "ex": "x取0,1,2"},
        {"q": "以下哪个是合法的变量名？", "op": ["2name", "my_name", "my-name", "class"], "ci": 1, "ex": "变量名不能以数字开头"},
        {"q": "try语句的作用是？", "op": ["定义函数", "处理异常", "创建循环", "导入模块"], "ci": 1, "ex": "try/except用于异常处理"},
    ]
    results = []
    correct_count = 0
    for i, a in enumerate(answers):
        if i >= len(fb_qs):
            break
        q = fb_qs[i]
        is_correct = (a == q["ci"])
        if is_correct:
            correct_count += 1
        ua = q["op"][a] if isinstance(a, int) and a < len(q["op"]) else "?"
        results.append({"question_num": i+1, "question": q["q"], "user_answer": ua, "correct_answer": q["op"][q["ci"]], "is_correct": is_correct, "explanation": q["ex"]})
    total = len(fb_qs)
    score = int(correct_count / total * 100) if total > 0 else 0
    return {"score": score, "correct": correct_count, "total": total, "passed": score >= 60, "results": results, "feedback": ""}

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

