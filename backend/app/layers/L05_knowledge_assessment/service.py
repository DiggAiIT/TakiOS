"""Layer 5: Business logic for knowledge assessment."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.events import EventBus
from app.layers.L05_knowledge_assessment.models import (
    Answer,
    Exam,
    ExamAttempt,
    ExamQuestion,
    QuestionBank,
)
from app.shared.exceptions import NotFoundError


async def get_exams_by_module(db: AsyncSession, module_id: uuid.UUID) -> list[Exam]:
    result = await db.execute(
        select(Exam).where(Exam.module_id == module_id)
    )
    return list(result.scalars().all())


async def start_exam(
    db: AsyncSession, exam_id: uuid.UUID, user_id: uuid.UUID
) -> tuple[ExamAttempt, list[QuestionBank]]:
    """Start a new exam attempt and return the questions."""
    exam = await db.get(Exam, exam_id)
    if not exam:
        raise NotFoundError("Exam", str(exam_id))

    # Create attempt
    attempt = ExamAttempt(exam_id=exam_id, user_id=user_id)
    db.add(attempt)
    await db.flush()

    # Get questions
    result = await db.execute(
        select(ExamQuestion)
        .where(ExamQuestion.exam_id == exam_id)
        .order_by(ExamQuestion.position)
    )
    exam_questions = result.scalars().all()
    question_ids = [eq.question_id for eq in exam_questions]

    questions_result = await db.execute(
        select(QuestionBank).where(QuestionBank.id.in_(question_ids))
    )
    return attempt, list(questions_result.scalars().all())


async def submit_exam(
    db: AsyncSession,
    attempt_id: uuid.UUID,
    answers: list[dict],
) -> ExamAttempt:
    """Submit answers and auto-grade multiple choice questions."""
    attempt = await db.get(ExamAttempt, attempt_id)
    if not attempt:
        raise NotFoundError("ExamAttempt", str(attempt_id))

    total_score = 0.0
    total_possible = 0.0

    for ans in answers:
        question = await db.get(QuestionBank, ans["question_id"])
        if not question:
            continue

        score = None
        if question.question_type.value == "multiple_choice":
            correct = question.correct_answer.get("answer")
            given = ans["answer_data"].get("answer")
            score = 1.0 if correct == given else 0.0
            total_score += score
        total_possible += 1.0

        answer = Answer(
            attempt_id=attempt_id,
            question_id=ans["question_id"],
            answer_data=ans["answer_data"],
            score=score,
        )
        db.add(answer)

    if total_possible > 0:
        attempt.total_score = (total_score / total_possible) * 100
        attempt.passed = attempt.total_score >= 50.0

    await db.flush()

    # Publish event for cross-layer communication (pass db for same-transaction updates)
    await EventBus.publish("exam_completed", {
        "db": db,
        "user_id": str(attempt.user_id),
        "exam_id": str(attempt.exam_id),
        "score": attempt.total_score,
        "passed": attempt.passed,
    })

    return attempt


async def generate_contextual_exam(
    db: AsyncSession,
    module_id: uuid.UUID,
    project_context: str,
    question_count: int,
    user_id: uuid.UUID,
) -> Exam:
    """Generate a personalized, project-contextual exam using AI."""
    from app.core.ai.client import get_ai_client
    from app.layers.L03_subjects_modules.models import Module
    import json

    module = await db.get(Module, module_id)
    if not module:
        raise NotFoundError("Module", str(module_id))

    prompt = (
        f"Create an exam with {question_count} questions for the module '{module.name_de}'. "
        f"The student is actively working on the medical device project: '{project_context}'.\n"
        "IMPORTANT: The questions must not be purely abstract. They MUST be directly framed "
        "around the student's project context. (e.g., 'For your EKG wearable, calculate...').\n"
        "Return the questions as a JSON array of objects, where each object has:\n"
        "- question_de: string\n"
        "- answer_options: object with a,b,c,d as keys and text as values\n"
        "- correct_answer: object with 'answer' key (e.g. 'a')\n"
    )

    system = "You are TakiOS Assessment Engine. Generate project-contextual multiple choice exam questions in strict JSON array format."

    ai_client = get_ai_client()
    response_text = await ai_client.generate_text(prompt=prompt, system=system, max_tokens=2000)

    try:
        data = json.loads(response_text)
    except Exception:
        # Fallback if AI fails to return strict JSON
        data = []

    # Create Exam
    exam = Exam(
        module_id=module_id,
        title=f"Contextual Exam: {module.name_de} ({project_context[:20]}...)",
        created_by=user_id,
    )
    db.add(exam)
    await db.flush()

    # Create Questions & Link to Exam
    for idx, q_data in enumerate(data, start=1):
        # We assume the module_unit_id is not strictly required or we map to first unit
        # For this prototype, we'll just link it conceptually. To satisfy DB, 
        # let's just grab any module unit of this module.
        from app.layers.L03_subjects_modules.models import ModuleUnit
        result = await db.execute(select(ModuleUnit).where(ModuleUnit.module_id == module_id).limit(1))
        unit = result.scalar_one_or_none()
        
        q = QuestionBank(
            module_unit_id=unit.id if unit else module_id,  # fallback if unit missing
            question_type="multiple_choice",
            question_de=q_data.get("question_de", "Fehlende Frage"),
            answer_options=q_data.get("answer_options", {}),
            correct_answer=q_data.get("correct_answer", {"answer": "a"})
        )
        db.add(q)
        await db.flush()

        eq = ExamQuestion(
            exam_id=exam.id,
            question_id=q.id,
            position=idx,
            points=1.0
        )
        db.add(eq)

    await db.flush()
    return exam

