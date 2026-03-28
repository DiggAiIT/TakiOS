import pytest

from app.api.endpoints.grade import get_grading_service
from app.main import app


class StubGradingService:
    async def grade_submission(self, fact: str, student_response: str, rubric: str, project_context=None):
        return {
            "score": 8.5,
            "reasoning": f"Matched fact '{fact}'",
            "feedback": f"Improve response '{student_response}' with rubric '{rubric}'",
        }


class FailingGradingService:
    async def grade_submission(self, fact: str, student_response: str, rubric: str, project_context=None):
        raise RuntimeError("provider down")


@pytest.mark.asyncio
async def test_grade_endpoint_returns_structured_payload(async_client):
    app.dependency_overrides[get_grading_service] = lambda: StubGradingService()

    response = await async_client.post(
        "/api/v1/grade/",
        json={
            "submission_id": "sub-1",
            "fact": "The sensor requires calibration before use.",
            "student_response": "The sensor should be calibrated before use.",
            "rubric": "Accuracy",
            "project_context": "Wearable ECG",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["score"] == 8.5
    assert "Matched fact" in payload["reasoning"]


@pytest.mark.asyncio
async def test_grade_endpoint_returns_safe_error_message(async_client):
    app.dependency_overrides[get_grading_service] = lambda: FailingGradingService()

    response = await async_client.post(
        "/api/v1/grade/",
        json={
            "submission_id": "sub-2",
            "fact": "Use a clean reference signal.",
            "student_response": "No answer",
            "rubric": "Completeness",
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 500
    assert response.json()["detail"] == "Grading request failed"