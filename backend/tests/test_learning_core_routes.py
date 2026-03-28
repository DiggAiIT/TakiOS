from collections.abc import AsyncIterator
from types import SimpleNamespace
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.auth.dependencies import get_current_user
from app.database import get_db
from app.layers.L01_level_selection import router as level_router
from app.layers.L02_tech_units import router as tech_unit_router
from app.layers.L03_subjects_modules import router as subject_router
from app.layers.L04_content_eselsbruecken import router as content_router
from app.layers.L05_knowledge_assessment import router as assessment_router
from app.main import app


class DummySession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.fixture
async def learning_client() -> AsyncIterator[AsyncClient]:
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
async def test_level_routes_return_pyramid_payload(learning_client, monkeypatch):
    level_id = uuid4()

    async def stub_get_all_levels(_db):
        return [
            {
                "id": str(level_id),
                "parent_id": None,
                "name_de": "Elektronik",
                "name_en": "Electronics",
                "description_de": "Grundlagen",
                "description_en": "Basics",
                "pyramid_position": 1,
                "icon_url": None,
                "unlock_criteria": None,
            }
        ]

    async def stub_get_user_progress(_db, _user_id):
        return {str(level_id): "completed"}

    monkeypatch.setattr(level_router.service, "get_all_levels", stub_get_all_levels)
    monkeypatch.setattr(level_router.service, "get_user_progress", stub_get_user_progress)

    response = await learning_client.get("/api/v1/levels/pyramid")

    assert response.status_code == 200
    payload = response.json()
    assert payload["levels"][0]["name_de"] == "Elektronik"
    assert payload["progress"][str(level_id)] == "completed"


@pytest.mark.asyncio
async def test_tech_unit_routes_filter_by_level(learning_client, monkeypatch):
    level_id = uuid4()

    async def stub_get_units_by_level(_db, level_id_arg):
        return [
            {
                "id": str(uuid4()),
                "level_id": str(level_id_arg),
                "name_de": "ADC",
                "name_en": "ADC",
                "description_de": "Wandler",
                "description_en": "Converter",
                "io_spec": {"input": "analog", "output": "digital"},
                "limitations": "Noise",
            }
        ]

    monkeypatch.setattr(tech_unit_router.service, "get_units_by_level", stub_get_units_by_level)

    response = await learning_client.get("/api/v1/tech-units/", params={"level_id": str(level_id)})

    assert response.status_code == 200
    assert response.json()[0]["io_spec"]["output"] == "digital"


@pytest.mark.asyncio
async def test_subject_module_detail_route_returns_units(learning_client, monkeypatch):
    module_id = uuid4()
    subject_id = uuid4()
    unit_id = uuid4()

    async def stub_get_module_detail(_db, module_id_arg):
        return {
            "id": str(module_id_arg),
            "subject_id": str(subject_id),
            "code": "MT101",
            "name_de": "Medizintechnik 1",
            "name_en": "Biomedical Engineering 1",
            "semester": 1,
            "credits": 5,
            "description_de": "Beschreibung",
            "description_en": "Description",
            "units": [
                {
                    "id": str(unit_id),
                    "position": 1,
                    "title_de": "Einführung",
                    "title_en": "Introduction",
                }
            ],
        }

    monkeypatch.setattr(subject_router.service, "get_module_detail", stub_get_module_detail)

    response = await learning_client.get(f"/api/v1/subjects/modules/{module_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == "MT101"
    assert payload["units"][0]["title_de"] == "Einführung"


@pytest.mark.asyncio
async def test_content_route_returns_body_and_mnemonics(learning_client, monkeypatch):
    content_id = uuid4()
    unit_id = uuid4()

    async def stub_get_content_with_body(_db, _unit_id):
        return SimpleNamespace(id=content_id, module_unit_id=unit_id), "## Inhalt"

    async def stub_get_mnemonics_for_content(_db, content_id_arg, _user_id):
        return [
            {
                "id": str(uuid4()),
                "content_id": str(content_id_arg),
                "mnemonic_text": "Merksatz",
                "mnemonic_type": "analogy",
                "language": "de",
                "ai_generated": True,
                "effectiveness_score": None,
            }
        ]

    monkeypatch.setattr(content_router.service, "get_content_with_body", stub_get_content_with_body)
    monkeypatch.setattr(content_router.service, "get_mnemonics_for_content", stub_get_mnemonics_for_content)

    response = await learning_client.get(f"/api/v1/content/unit/{unit_id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["body_markdown"] == "## Inhalt"
    assert payload["mnemonics"][0]["mnemonic_text"] == "Merksatz"


@pytest.mark.asyncio
async def test_assessment_routes_return_exam_list(learning_client, monkeypatch):
    module_id = uuid4()

    async def stub_get_exams_by_module(_db, module_id_arg):
        return [
            {
                "id": str(uuid4()),
                "module_id": str(module_id_arg),
                "title": "Grundlagenprüfung",
                "exam_type": "digital",
                "time_limit_minutes": 30,
            }
        ]

    monkeypatch.setattr(assessment_router.service, "get_exams_by_module", stub_get_exams_by_module)

    response = await learning_client.get("/api/v1/assessment/exams", params={"module_id": str(module_id)})

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["title"] == "Grundlagenprüfung"
    assert payload[0]["exam_type"] == "digital"