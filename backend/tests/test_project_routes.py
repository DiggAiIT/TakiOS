from collections.abc import AsyncIterator
from types import SimpleNamespace
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.auth.dependencies import get_current_user
from app.database import get_db
from app.main import app


class DummySession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.fixture
async def project_client() -> AsyncIterator[AsyncClient]:
    async def override_get_db():
        yield DummySession()

    async def override_current_user():
        return SimpleNamespace(id=uuid4(), is_active=True)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_artifact_rejects_too_large_file(project_client):
    payload = b"x" * (10 * 1024 * 1024 + 1)

    response = await project_client.post(
        f"/api/v1/projects/{uuid4()}/artifacts",
        files={"file": ("artifact.bin", payload, "application/octet-stream")},
    )

    assert response.status_code == 413
    assert "Artifact exceeds" in response.json()["detail"]