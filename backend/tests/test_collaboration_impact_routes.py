from collections.abc import AsyncIterator
from types import SimpleNamespace
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.auth.dependencies import get_current_user
from app.database import get_db
from app.layers.L07_faculty_collaboration import router as collaboration_router
from app.layers.L13_social_engineering_impact import router as impact_router
from app.main import app


class DummySession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.fixture
async def collaboration_client() -> AsyncIterator[AsyncClient]:
    async def override_get_db():
        yield DummySession()

    user = SimpleNamespace(id=uuid4(), is_active=True)

    async def override_current_user():
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_collaboration_list_faculty_returns_profiles(collaboration_client, monkeypatch):
    async def stub_get_available_faculty(_db):
        return [
            {
                "id": str(uuid4()),
                "user_id": str(uuid4()),
                "department": "Regulatory Affairs",
                "expertise_areas": {"areas": ["MDR", "IEC 62304"]},
                "available_for_review": True,
            }
        ]

    monkeypatch.setattr(collaboration_router.service, "get_available_faculty", stub_get_available_faculty)

    response = await collaboration_client.get("/api/v1/collaboration/faculty")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["department"] == "Regulatory Affairs"
    assert payload[0]["available_for_review"] is True


@pytest.mark.asyncio
async def test_collaboration_incoming_reviews_returns_empty_without_profile(collaboration_client, monkeypatch):
    async def stub_get_faculty_profile(_db, _user_id):
        return None

    monkeypatch.setattr(collaboration_router.service, "get_faculty_profile", stub_get_faculty_profile)

    response = await collaboration_client.get("/api/v1/collaboration/reviews/incoming")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_collaboration_request_review_passes_current_user(collaboration_client, monkeypatch):
    captured: dict[str, object] = {}
    project_id = uuid4()
    faculty_id = uuid4()

    async def stub_create_review_request(_db, project_id_arg, faculty_id_arg, user_id_arg):
        captured["project_id"] = project_id_arg
        captured["faculty_id"] = faculty_id_arg
        captured["user_id"] = user_id_arg
        return {
            "id": str(uuid4()),
            "project_id": str(project_id_arg),
            "faculty_id": str(faculty_id_arg),
            "requested_by": str(user_id_arg),
            "status": "pending",
            "review_text": None,
            "created_at": "2026-03-27T10:00:00Z",
        }

    monkeypatch.setattr(collaboration_router.service, "create_review_request", stub_create_review_request)

    response = await collaboration_client.post(
        "/api/v1/collaboration/reviews",
        json={"project_id": str(project_id), "faculty_id": str(faculty_id)},
    )

    assert response.status_code == 201
    assert response.json()["status"] == "pending"
    assert captured["project_id"] == project_id
    assert captured["faculty_id"] == faculty_id
    assert captured["user_id"] is not None


@pytest.mark.asyncio
async def test_collaboration_project_reviews_route_uses_authorized_service(collaboration_client, monkeypatch):
    project_id = uuid4()
    captured: dict[str, object] = {}

    async def stub_get_project_reviews_for_user(_db, project_id_arg, user_id_arg):
        captured["project_id"] = project_id_arg
        captured["user_id"] = user_id_arg
        return []

    monkeypatch.setattr(
        collaboration_router.service,
        "get_project_reviews_for_user",
        stub_get_project_reviews_for_user,
    )

    response = await collaboration_client.get(f"/api/v1/collaboration/reviews/project/{project_id}")

    assert response.status_code == 200
    assert captured["project_id"] == project_id
    assert captured["user_id"] is not None


@pytest.mark.asyncio
async def test_impact_list_assessments_returns_payload(collaboration_client, monkeypatch):
    async def stub_list_assessments(_db):
        return [
            {
                "id": str(uuid4()),
                "title": "Bias review",
                "category": "ethics",
                "description": "Check model bias exposure.",
                "risk_level": "medium",
                "mitigation": "Independent validation",
            }
        ]

    monkeypatch.setattr(impact_router.service, "list_assessments", stub_list_assessments)

    response = await collaboration_client.get("/api/v1/impact/assessments")

    assert response.status_code == 200
    assert response.json()[0]["category"] == "ethics"


@pytest.mark.asyncio
async def test_impact_submit_survey_response_passes_user(collaboration_client, monkeypatch):
    captured: dict[str, object] = {}
    survey_id = uuid4()

    async def stub_submit_survey_response(_db, data, user_id):
        captured["survey_id"] = data.survey_id
        captured["responses"] = data.responses
        captured["user_id"] = user_id
        return {
            "id": str(uuid4()),
            "survey_id": str(data.survey_id),
            "user_id": str(user_id),
            "responses": data.responses,
        }

    monkeypatch.setattr(impact_router.service, "submit_survey_response", stub_submit_survey_response)

    response = await collaboration_client.post(
        "/api/v1/impact/surveys/respond",
        json={"survey_id": str(survey_id), "responses": {"q1": "useful"}},
    )

    assert response.status_code == 201
    assert response.json()["responses"]["q1"] == "useful"
    assert captured["survey_id"] == survey_id
    assert captured["responses"] == {"q1": "useful"}
    assert captured["user_id"] is not None