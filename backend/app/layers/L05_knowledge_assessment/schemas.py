"""Layer 5: Request/response schemas."""

import uuid

from pydantic import BaseModel

from app.layers.L05_knowledge_assessment.models import (
    BloomLevel,
    Difficulty,
    ExamType,
    QuestionType,
)


class QuestionResponse(BaseModel):
    id: uuid.UUID
    question_type: QuestionType
    question_de: str
    question_en: str
    answer_options: dict | None
    difficulty: Difficulty
    bloom_level: BloomLevel

    model_config = {"from_attributes": True}


class ExamResponse(BaseModel):
    id: uuid.UUID
    module_id: uuid.UUID
    title: str
    exam_type: ExamType
    time_limit_minutes: int | None

    model_config = {"from_attributes": True}


class StartExamResponse(BaseModel):
    attempt_id: uuid.UUID
    questions: list[QuestionResponse]


class SubmitAnswerRequest(BaseModel):
    question_id: uuid.UUID
    answer_data: dict


class SubmitExamRequest(BaseModel):
    answers: list[SubmitAnswerRequest]


class ExamResultResponse(BaseModel):
    attempt_id: uuid.UUID
    total_score: float | None
    passed: bool | None
    answers: list[dict] = []

    model_config = {"from_attributes": True}

class GenerateContextualExamRequest(BaseModel):
    module_id: uuid.UUID
    project_context: str
    question_count: int = 5

