import logging

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.submission import GradingRequest, GradingResponse
from app.services.grading_service import GradingService

router = APIRouter()
logger = logging.getLogger(__name__)

def get_grading_service() -> GradingService:
    return GradingService()

@router.post("/", response_model=GradingResponse)
async def grade_submission(
    request: GradingRequest,
    service: GradingService = Depends(get_grading_service),
):
    try:
        result = await service.grade_submission(
            fact=request.fact,
            student_response=request.student_response,
            rubric=request.rubric,
            project_context=request.project_context
        )
        return GradingResponse(
            score=result.get("score", 0.0),
            reasoning=result.get("reasoning", "No reasoning provided"),
            feedback=result.get("feedback", "")
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Grading request failed", exc_info=exc)
        raise HTTPException(status_code=500, detail="Grading request failed") from exc
