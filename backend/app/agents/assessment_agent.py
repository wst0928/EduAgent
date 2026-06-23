"""Assessment Agent: creates quizzes, evaluates understanding, tracks mastery."""
from __future__ import annotations

from typing import Any

from app.agents.base_agent import BaseAgent
from app.models.resource import (
    FlashcardContent,
    LearningResource,
    QuizContent,
    QuizQuestion,
    ResourceType,
)
from app.services.memory_service import memory_service


PROMPT = """你是一位教育测评专家，擅长设计有效的评估工具来衡量学习者的掌握程度。
你的职责：
1. 根据学习内容生成测验题目（选择题、判断题）
2. 评估学习者的回答并提供详细的反馈和解析
3. 分析学习者的薄弱环节并给出改进建议
4. 生成复习闪卡辅助记忆
5. 追踪学习者的知识掌握度
"""


class AssessmentAgent(BaseAgent):
    """Generates assessments and evaluates learner comprehension."""

    def __init__(self) -> None:
        super().__init__(
            name="AssessmentAgent",
            description="生成测验、评估理解程度、追踪掌握度",
            system_prompt=PROMPT,
        )

    async def process(self, context: dict[str, Any]) -> dict[str, Any]:
        action = context.get("action", "generate_quiz")

        if action == "generate_quiz":
            return await self._generate_quiz(context)
        elif action == "evaluate_answer":
            return await self._evaluate_answer(context)
        elif action == "generate_flashcards":
            return await self._generate_flashcards(context)
        elif action == "analyze_weaknesses":
            return await self._analyze_weaknesses(context)
        else:
            return {"error": f"Unknown action: {action}"}

    async def _generate_quiz(self, context: dict[str, Any]) -> dict[str, Any]:
        topic = context.get("topic", "")
        difficulty = context.get("difficulty", "beginner")
        num_questions = context.get("num_questions", 5)

        result = await self._llm_structured([
            {"role": "user",
             "content": f"""为以下学习内容生成测验题目。

主题：{topic}
难度：{difficulty}
题目数量：{num_questions}

要求：
- 题目覆盖核心知识点
- 每道题给出4个选项
- 标注正确答案（0-based索引）
- 提供答案解析
- 标注每道题的难度（1-5）

返回JSON格式：
{{
  "title": "测验标题",
  "questions": [
    {{
      "question": "题目文本",
      "options": ["A选项", "B选项", "C选项", "D选项"],
      "correct_index": 0,
      "explanation": "解析",
      "difficulty": 1
    }}
  ]
}}"""
            }])

        questions_data = result.get("questions", [])
        questions = [
            QuizQuestion(
                question=q.get("question", ""),
                options=q.get("options", ["", "", "", ""]),
                correct_index=q.get("correct_index", 0),
                explanation=q.get("explanation", ""),
                difficulty=q.get("difficulty", 1),
            )
            for q in questions_data
        ]

        quiz_content = QuizContent(
            title=result.get("title", f"{topic} - 测验"),
            questions=questions,
            passing_score=60,
        )

        resource = LearningResource(
            title=f"{topic} - 测验评估",
            resource_type=ResourceType.quiz,
            quiz_content=quiz_content,
        )
        memory_service.save_resource(resource)

        return {
            "resource_id": resource.id,
            "quiz": quiz_content.model_dump(),
        }

    async def _evaluate_answer(self, context: dict[str, Any]) -> dict[str, Any]:
        quiz_id = context.get("quiz_id", "")
        user_answers = context.get("answers", [])

        resource = memory_service.get_resource(quiz_id)
        if not resource or not resource.quiz_content:
            return {"error": "测验未找到"}

        quiz = resource.quiz_content
        results = []
        correct_count = 0

        for i, (question, answer_idx) in enumerate(zip(quiz.questions, user_answers)):
            is_correct = answer_idx == question.correct_index
            if is_correct:
                correct_count += 1
            results.append({
                "question_num": i + 1,
                "question": question.question,
                "user_answer": question.options[answer_idx]
                                 if answer_idx < len(question.options) else "未作答",
                "correct_answer": question.options[question.correct_index],
                "is_correct": is_correct,
                "explanation": question.explanation,
            })

        total = len(quiz.questions)
        score = int(correct_count / total * 100) if total > 0 else 0
        passed = score >= quiz.passing_score

        feedback = ""
        if not passed:
            weak_areas = [r["question"] for r in results if not r["is_correct"]]
            feedback_result = await self._llm_chat([
                {"role": "user",
                 "content": f"""学习者在以下题目上答错了，请给出针对性的学习建议：

答错题目：
{chr(10).join(f"- {q}" for q in weak_areas)}

请给出简短的学习建议，指出需要加强的方面。"""}
            ])
            feedback = feedback_result

        return {
            "score": score,
            "correct": correct_count,
            "total": total,
            "passed": passed,
            "passing_score": quiz.passing_score,
            "results": results,
            "feedback": feedback,
        }

    async def _generate_flashcards(self, context: dict[str, Any]) -> dict[str, Any]:
        topic = context.get("topic", "")
        num_cards = context.get("num_cards", 10)

        result = await self._llm_structured([
            {"role": "user",
             "content": f"""为以下学习主题生成{num_cards}张记忆闪卡。

主题：{topic}

每张闪卡正面是一个问题/概念，背面是答案/定义。
适合快速复习。

返回JSON格式：
{{
  "cards": [
    {{"front": "问题或概念", "back": "答案或定义"}}
  ]
}}"""
            }])

        cards = result.get("cards", [])
        flashcard_content = FlashcardContent(cards=cards)

        resource = LearningResource(
            title=f"{topic} - 记忆闪卡",
            resource_type=ResourceType.flashcard,
            flashcard_content=flashcard_content,
        )
        memory_service.save_resource(resource)

        return {
            "resource_id": resource.id,
            "cards": cards,
        }

    async def _analyze_weaknesses(self, context: dict[str, Any]) -> dict[str, Any]:
        user_id = context.get("user_id", "default")
        topic = context.get("topic", "")
        quiz_results = context.get("quiz_results", [])

        result = await self._llm_structured([
            {"role": "user",
             "content": f"""分析学习者的知识薄弱环节。

主题：{topic}
测验结果摘要：{str(quiz_results)[:2000]}

返回JSON格式：
{{
  "overall_assessment": "总体评估",
  "weak_areas": [
    {{"area": "薄弱领域", "description": "具体薄弱点", "suggested_action": "改进建议"}}
  ],
  "strong_areas": ["掌握较好的领域"],
  "recommended_focus": "下一步学习建议"
}}"""
            }])
        return result
