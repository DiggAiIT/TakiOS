from pydantic import BaseModel, Field


class GradingRequest(BaseModel):
    submission_id: str
    fact: str
    student_response: str
    rubric: str
    project_context: str | None = None


class GradingResponse(BaseModel):
    score: float = Field(..., ge=0, le=10, description="Grade from 0 to 10")
    reasoning: str
    feedback: str
    confidence_score: float = Field(
        default=0.0,
        ge=0,
        le=1,
        description="AI confidence in the grading (0.0–1.0). 0.0 = fallback/heuristic.",
    )
    matched_concepts: list[str] = Field(
        default_factory=list,
        description="Key concepts from the fact that the student correctly addressed.",
    )
    improvement_hints: list[str] = Field(
        default_factory=list,
        description="Specific, actionable suggestions for the student to improve.",
    )
    model_used: str = Field(
        default="local-fallback",
        description="Which AI model produced this grading.",
    )
