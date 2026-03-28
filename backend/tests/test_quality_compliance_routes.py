from collections.abc import AsyncIterator
from types import SimpleNamespace
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status

from app.core.auth.dependencies import get_current_user
from app.database import get_db
from app.layers.L11_legal_compliance import router as compliance_router
from app.layers.L12_quality_management import router as quality_router
from app.main import app


class DummySession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.fixture
async def admin_client() -> AsyncIterator[AsyncClient]:
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
async def test_quality_dashboard_route_returns_dashboard(admin_client, monkeypatch):
    async def stub_get_dashboard(_db):
        return {
            "metrics": [
                {
                    "metric_id": str(uuid4()),
                    "name": "Testabdeckung",
                    "target_value": 90.0,
                    "latest_value": 87.5,
                    "unit": "%",
                }
            ],
            "total_feedback_count": 4,
            "average_rating": 4.5,
        }

    monkeypatch.setattr(quality_router.service, "get_dashboard", stub_get_dashboard)

    response = await admin_client.get("/api/v1/quality/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_feedback_count"] == 4
    assert payload["metrics"][0]["name"] == "Testabdeckung"


@pytest.mark.asyncio
async def test_quality_feedback_route_passes_user_to_service(admin_client, monkeypatch):
    captured: dict[str, object] = {}

    async def stub_create_feedback(_db, data, user_id):
        captured["user_id"] = user_id
        captured["category"] = data.category
        return {
            "id": str(uuid4()),
            "user_id": str(user_id),
            "category": data.category,
            "text": data.text,
            "rating": data.rating,
        }

    monkeypatch.setattr(quality_router.service, "create_feedback", stub_create_feedback)

    response = await admin_client.post(
        "/api/v1/quality/feedback",
        json={"category": "usability", "text": "Hilfreich", "rating": 5},
    )

    assert response.status_code == 201
    assert response.json()["category"] == "usability"
    assert captured["category"] == "usability"
    assert captured["user_id"] is not None


@pytest.mark.asyncio
async def test_compliance_requirements_route_forwards_framework_filter(admin_client, monkeypatch):
    captured: dict[str, object] = {}

    async def stub_list_requirements(_db, framework=None):
        captured["framework"] = framework
        return [
            {
                "id": str(uuid4()),
                "framework": framework or "MDR",
                "clause": "Art. 10",
                "title": "QMS",
                "description": "Maintain a documented quality management system.",
                "applies_to": "all",
            }
        ]

    monkeypatch.setattr(compliance_router.service, "list_requirements", stub_list_requirements)

    response = await admin_client.get("/api/v1/compliance/requirements", params={"framework": "MDR"})

    assert response.status_code == 200
    assert captured["framework"] == "MDR"
    assert response.json()[0]["framework"] == "MDR"


@pytest.mark.asyncio
async def test_compliance_evidence_route_passes_current_user(admin_client, monkeypatch):
    captured: dict[str, object] = {}
    requirement_id = uuid4()

    async def stub_create_evidence(_db, data, user_id):
        captured["user_id"] = user_id
        captured["requirement_id"] = data.requirement_id
        return {
            "id": str(uuid4()),
            "requirement_id": str(data.requirement_id),
            "evidence_type": data.evidence_type,
            "description": data.description,
            "verified_by": None,
            "verified_at": None,
        }

    monkeypatch.setattr(compliance_router.service, "create_evidence", stub_create_evidence)

    response = await admin_client.post(
        "/api/v1/compliance/evidence",
        json={
            "requirement_id": str(requirement_id),
            "evidence_type": "document",
            "description": "Design history file updated.",
        },
    )

    assert response.status_code == 201
    assert response.json()["evidence_type"] == "document"
    assert captured["requirement_id"] == requirement_id
    assert captured["user_id"] is not None


@pytest.mark.asyncio
async def test_quality_dashboard_requires_auth(monkeypatch):
    async def override_get_db():
        yield DummySession()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides.pop(get_current_user, None)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/quality/dashboard")

    app.dependency_overrides.clear()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_compliance_status_requires_auth(monkeypatch):
    async def override_get_db():
        yield DummySession()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides.pop(get_current_user, None)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/compliance/status")

    app.dependency_overrides.clear()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED