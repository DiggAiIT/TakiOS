"""Layer 5: API endpoints for knowledge assessment."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_db
from app.layers.L05_knowledge_assessment import service
from app.layers.L05_knowledge_assessment.schemas import (
    ExamResponse,
    ExamResultResponse,
    GenerateContextualExamRequest,
    StartExamResponse,
    SubmitExamRequest,
)

router = APIRouter()


@router.get("/exams", response_model=list[ExamResponse])
async def list_exams(
    module_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """List available exams for a module."""
    return await service.get_exams_by_module(db, module_id)


@router.post("/exams/{exam_id}/start", response_model=StartExamResponse)
async def start_exam(
    exam_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Start a new exam attempt."""
    attempt, questions = await service.start_exam(db, exam_id, user.id)
    return StartExamResponse(attempt_id=attempt.id, questions=questions)


@router.post("/attempts/{attempt_id}/submit", response_model=ExamResultResponse)
async def submit_exam(
    attempt_id: uuid.UUID,
    data: SubmitExamRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit exam answers for grading."""
    answers = [{"question_id": a.question_id, "answer_data": a.answer_data} for a in data.answers]
    attempt = await service.submit_exam(db, attempt_id, answers)
    return ExamResultResponse(
        attempt_id=attempt.id,
        total_score=attempt.total_score,
        passed=attempt.passed,
    )

@router.post("/exams/contextual", response_model=ExamResponse)
async def generate_contextual_exam(
    data: GenerateContextualExamRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Generate a contextual exam for a specific module customized dynamically for a student's project."""
    return await service.generate_contextual_exam(db, data.module_id, data.project_context, data.question_count, user.id)

