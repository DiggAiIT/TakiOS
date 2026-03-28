"""Layer 5: Assessment models — exams, questions, attempts, grading."""

import enum
import uuid

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import AuditBase


class QuestionType(str, enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    FREE_TEXT = "free_text"
    DIAGRAM_LABEL = "diagram_label"
    MATCHING = "matching"


class Difficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class BloomLevel(str, enum.Enum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class ExamType(str, enum.Enum):
    DIGITAL = "digital"
    PEN_AND_PAPER = "pen_and_paper"
    HYBRID = "hybrid"


class QuestionBank(AuditBase):
    """A question in the question bank."""

    __tablename__ = "question_bank"

    module_unit_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("module_unit.id"), nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), nullable=False)
    question_de: Mapped[str] = mapped_column(Text, nullable=False)
    question_en: Mapped[str] = mapped_column(Text, default="")
    answer_options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    correct_answer: Mapped[dict] = mapped_column(JSONB, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), default=Difficulty.MEDIUM)
    bloom_level: Mapped[BloomLevel] = mapped_column(Enum(BloomLevel), default=BloomLevel.UNDERSTAND)


class Exam(AuditBase):
    """An exam composed of questions from the bank."""

    __tablename__ = "exam"

    module_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("module.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    exam_type: Mapped[ExamType] = mapped_column(Enum(ExamType), default=ExamType.DIGITAL)
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)

    questions = relationship("ExamQuestion", back_populates="exam", order_by="ExamQuestion.position")


class ExamQuestion(AuditBase):
    """Links a question to an exam with position and point value."""

    __tablename__ = "exam_question"

    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam.id"), nullable=False)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("question_bank.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[float] = mapped_column(Float, default=1.0)

    exam = relationship("Exam", back_populates="questions")


class ExamAttempt(AuditBase):
    """A student's attempt at an exam."""

    __tablename__ = "exam_attempt"

    exam_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    total_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    scan_file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)


class Answer(AuditBase):
    """A student's answer to a specific question in an exam attempt."""

    __tablename__ = "answer"

    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("exam_attempt.id"), nullable=False)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("question_bank.id"), nullable=False)
    answer_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
