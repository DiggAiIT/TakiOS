from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.layers.L06_project_creation import service
from app.layers.L06_project_creation.models import Project, ProjectArtifact
from app.shared.exceptions import ForbiddenError, NotFoundError


class _ScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class FakeSession:
    def __init__(self, execute_value=None, get_values=None):
        self.execute_value = execute_value
        self.get_values = get_values or {}
        self.deleted = []
        self.added = []
        self.flushed = False

    async def execute(self, _statement):
        return _ScalarResult(self.execute_value)

    async def get(self, model, identifier):
        return self.get_values.get((model, identifier))

    async def delete(self, instance):
        self.deleted.append(instance)

    def add(self, instance):
        self.added.append(instance)

    async def flush(self):
        self.flushed = True


@pytest.mark.asyncio
async def test_get_project_rejects_foreign_owner():
    owner_id = uuid4()
    other_user_id = uuid4()
    project = SimpleNamespace(id=uuid4(), created_by=owner_id, milestones=[], artifacts=[])
    db = FakeSession(execute_value=project)

    with pytest.raises(ForbiddenError):
        await service.get_project(db, project.id, other_user_id)


@pytest.mark.asyncio
async def test_delete_artifact_requires_owner():
    owner_id = uuid4()
    project_id = uuid4()
    artifact_id = uuid4()
    artifact = SimpleNamespace(id=artifact_id, project_id=project_id, file_url="projects/x/file.txt")
    project = SimpleNamespace(id=project_id, created_by=owner_id, milestones=[], artifacts=[])
    db = FakeSession(
        get_values={
            (ProjectArtifact, artifact_id): artifact,
        },
        execute_value=project,
    )

    with pytest.raises(ForbiddenError):
        await service.delete_artifact(db, artifact_id, uuid4())


@pytest.mark.asyncio
async def test_delete_artifact_removes_artifact_for_owner():
    owner_id = uuid4()
    project_id = uuid4()
    artifact_id = uuid4()
    artifact = SimpleNamespace(id=artifact_id, project_id=project_id, file_url="projects/x/file.txt")
    project = SimpleNamespace(id=project_id, created_by=owner_id, milestones=[], artifacts=[])
    db = FakeSession(
        get_values={
            (ProjectArtifact, artifact_id): artifact,
        },
        execute_value=project,
    )

    deleted_artifact = await service.delete_artifact(db, artifact_id, owner_id)

    assert deleted_artifact is artifact
    assert db.deleted == [artifact]
    assert db.flushed is True


@pytest.mark.asyncio
async def test_delete_artifact_raises_for_unknown_artifact():
    db = FakeSession(get_values={})

    with pytest.raises(NotFoundError):
        await service.delete_artifact(db, uuid4(), uuid4())