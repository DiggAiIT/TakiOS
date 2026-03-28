"""Unit tests for all service layer functions with mocked DB sessions.

Uses a queue-based MockSession / MockResult so each service function
can be tested without a real database.
"""

import uuid
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ── Mock infrastructure ──────────────────────────────────────────────


class MockResult:
    """Simulates an SQLAlchemy async execute result."""

    def __init__(self, data: Any = None):
        # Normalise: list stays list, single value gets wrapped
        if isinstance(data, list):
            self._rows = data
        elif data is None:
            self._rows = []
        else:
            self._rows = [data]

    def scalars(self) -> "MockResult":
        return self

    def all(self) -> list:
        return self._rows

    def scalar_one_or_none(self) -> Any:
        return self._rows[0] if self._rows else None

    def scalar(self) -> Any:
        return self._rows[0] if self._rows else None


class MockSession:
    """Queue-based mock for AsyncSession.

    Call ``queue_execute(result, ...)`` to define what successive
    ``await db.execute(...)`` calls return.
    Call ``queue_get(obj, ...)`` to define what successive
    ``await db.get(...)`` calls return.
    """

    def __init__(self) -> None:
        self._execute_q: list[Any] = []
        self._get_q: list[Any] = []
        self.added: list[Any] = []
        self.deleted: list[Any] = []
        self.flushed = False

    def queue_execute(self, *results: Any) -> None:
        for r in results:
            self._execute_q.append(r)

    def queue_get(self, *objects: Any) -> None:
        for o in objects:
            self._get_q.append(o)

    async def execute(self, stmt: Any) -> MockResult:  # noqa: ARG002
        data = self._execute_q.pop(0) if self._execute_q else None
        return MockResult(data)

    async def get(self, model: Any, pk: Any) -> Any:  # noqa: ARG002
        return self._get_q.pop(0) if self._get_q else None

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def delete(self, obj: Any) -> None:
        self.deleted.append(obj)

    async def flush(self) -> None:
        self.flushed = True


# ── Pagination ───────────────────────────────────────────────────────


from app.shared.pagination import PaginatedResponse, PaginationParams


def test_pagination_params_defaults():
    p = PaginationParams()
    assert p.page == 1
    assert p.per_page == 20
    assert p.offset == 0


def test_pagination_params_offset():
    p = PaginationParams(page=3, per_page=10)
    assert p.offset == 20


def test_paginated_response_create_pages():
    resp = PaginatedResponse.create(items=list(range(5)), total=25, page=2, per_page=10)
    assert resp.pages == 3
    assert resp.page == 2
    assert resp.per_page == 10
    assert resp.total == 25


def test_paginated_response_create_partial_page():
    resp = PaginatedResponse.create(items=[], total=11, page=1, per_page=10)
    assert resp.pages == 2


def test_paginated_response_zero_per_page():
    # Edge case: per_page=0 should not divide by zero
    resp = PaginatedResponse.create(items=[], total=5, page=1, per_page=0)
    assert resp.pages == 0


# ── GradingService ───────────────────────────────────────────────────


from app.services.grading_service import GradingService


def test_fallback_grade_good_overlap():
    svc = GradingService()
    result = svc._fallback_grade(
        fact="Electrocardiogram measures heart electrical activity",
        student_response="Electrocardiogram measures heart electrical activity precisely",
        rubric="accuracy",
    )
    assert 0 <= result["score"] <= 10
    assert "reasoning" in result
    assert "feedback" in result


def test_fallback_grade_no_overlap():
    svc = GradingService()
    result = svc._fallback_grade(
        fact="Electrocardiogram measures electrical signals",
        student_response="Dogs bark loudly",
        rubric="accuracy",
    )
    # Length bonus can add a small amount; score must be very low
    assert result["score"] < 2.0


def test_fallback_grade_with_project_context():
    svc = GradingService()
    result = svc._fallback_grade(
        fact="Sensors detect physiological signals",
        student_response="Sensors are used to detect physiological signals in wearables",
        rubric="application",
        project_context="EKG Wearable for Athletes",
    )
    assert "Project context" in result["reasoning"]


@pytest.mark.asyncio
async def test_grade_submission_uses_fallback_when_no_client():
    svc = GradingService()
    svc.client = None  # force fallback
    result = await svc.grade_submission(
        fact="Signal processing filters noise",
        student_response="Signal processing filters noise from measurements",
        rubric="accuracy",
    )
    assert "score" in result
    assert "reasoning" in result


@pytest.mark.asyncio
async def test_grade_submission_with_ai_client():
    svc = GradingService()
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"score": 8.5, "reasoning": "Good answer", "feedback": "Expand more"}')]
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    svc.client = mock_client

    result = await svc.grade_submission(
        fact="EKG traces heart rhythm",
        student_response="EKG is used to trace the rhythm of the heart",
        rubric="accuracy",
    )
    assert result["score"] == 8.5
    assert result["reasoning"] == "Good answer"


@pytest.mark.asyncio
async def test_grade_submission_ai_fallback_on_error():
    svc = GradingService()
    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(side_effect=Exception("API error"))
    svc.client = mock_client

    # Should fall back to local grading after exhausting retries
    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await svc.grade_submission(
            fact="Signal processing filters noise",
            student_response="Signal processing is used for noise filtering",
            rubric="accuracy",
        )
    assert "score" in result


@pytest.mark.asyncio
async def test_grade_submission_retries_before_fallback():
    """Verifies that grade_submission retries _MAX_GRADE_RETRIES times on API error."""
    from app.services.grading_service import _MAX_GRADE_RETRIES

    svc = GradingService()
    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(side_effect=RuntimeError("rate_limited"))
    svc.client = mock_client

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await svc.grade_submission(
            fact="Blood pressure measurement",
            student_response="Systolic and diastolic pressure",
            rubric="accuracy",
        )

    assert mock_client.messages.create.call_count == _MAX_GRADE_RETRIES
    # Sleep called _MAX_GRADE_RETRIES - 1 times (between attempts)
    assert mock_sleep.call_count == _MAX_GRADE_RETRIES - 1
    assert "score" in result  # fallback result


@pytest.mark.asyncio
async def test_grade_submission_succeeds_on_second_retry():
    """Verifies that a successful response on retry 2 is returned without fallback."""
    svc = GradingService()
    mock_client = AsyncMock()
    good_response = MagicMock()
    good_response.content = [MagicMock(text='{"score": 7.0, "reasoning": "Retry worked", "feedback": "Good"}')]
    mock_client.messages.create = AsyncMock(
        side_effect=[RuntimeError("timeout"), good_response]
    )
    svc.client = mock_client

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await svc.grade_submission(
            fact="EKG measures cardiac activity",
            student_response="EKG traces the heart electrical rhythm",
            rubric="accuracy",
        )

    assert result["score"] == 7.0
    assert mock_client.messages.create.call_count == 2


# ── Auth service ─────────────────────────────────────────────────────


from app.core.auth.service import (
    create_access_token,
    decode_token,
    hash_password,
    register_user,
    verify_password,
)
from app.shared.exceptions import ConflictError, NotFoundError


def test_hash_and_verify_password():
    pw = "SuperSecret123!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed)


def test_verify_wrong_password():
    hashed = hash_password("correct")
    assert not verify_password("wrong", hashed)


def test_create_and_decode_token():
    from app.core.auth.models import User, UserRole

    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.role = UserRole.STUDENT

    token_resp = create_access_token(user)
    assert token_resp.access_token

    payload = decode_token(token_resp.access_token)
    assert payload.sub == str(user.id)


def test_decode_invalid_token_raises():
    with pytest.raises(NotFoundError):
        decode_token("not.a.valid.token")


@pytest.mark.asyncio
async def test_register_user_conflict():
    from app.core.auth.schemas import UserCreate

    db = MockSession()
    existing = MagicMock()
    db.queue_execute(existing)  # simulate found existing user

    data = UserCreate(email="taken@example.com", password="pass1234", full_name="Test")
    with pytest.raises(ConflictError):
        await register_user(db, data)


@pytest.mark.asyncio
async def test_register_user_success():
    from app.core.auth.schemas import UserCreate

    db = MockSession()
    db.queue_execute(None)  # no existing user

    data = UserCreate(email="new@example.com", password="pass1234", full_name="New User")
    user = await register_user(db, data)
    assert len(db.added) == 1
    assert db.flushed


# ── L01 Level Selection ──────────────────────────────────────────────


from app.layers.L01_level_selection.models import LevelStatus
from app.layers.L01_level_selection.service import (
    get_all_levels,
    get_user_progress,
    update_level_status,
)


@pytest.mark.asyncio
async def test_get_all_levels_returns_list():
    db = MockSession()
    level = SimpleNamespace(id=uuid.uuid4(), pyramid_position=1, name_de="Basis")
    db.queue_execute([level])

    result = await get_all_levels(db)
    assert result == [level]


@pytest.mark.asyncio
async def test_get_all_levels_empty():
    db = MockSession()
    db.queue_execute([])
    result = await get_all_levels(db)
    assert result == []


@pytest.mark.asyncio
async def test_get_user_progress():
    level_id = uuid.uuid4()
    db = MockSession()
    progress = SimpleNamespace(level_id=level_id, status=LevelStatus.COMPLETED)
    db.queue_execute([progress])

    result = await get_user_progress(db, uuid.uuid4())
    assert result[str(level_id)] == LevelStatus.COMPLETED


@pytest.mark.asyncio
async def test_update_level_status_existing():
    db = MockSession()
    user_id = uuid.uuid4()
    level_id = uuid.uuid4()
    existing = SimpleNamespace(user_id=user_id, level_id=level_id, status=LevelStatus.LOCKED)
    db.queue_execute(existing)  # scalar_one_or_none returns existing

    result = await update_level_status(db, user_id, level_id, LevelStatus.IN_PROGRESS)
    assert result.status == LevelStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_update_level_status_creates_new():
    db = MockSession()
    user_id = uuid.uuid4()
    level_id = uuid.uuid4()
    db.queue_execute(None)  # not found → create

    result = await update_level_status(db, user_id, level_id, LevelStatus.IN_PROGRESS)
    assert any(hasattr(obj, "status") for obj in db.added)
    assert db.flushed


# ── L02 Tech Units ───────────────────────────────────────────────────


from app.layers.L02_tech_units.service import (
    get_all_units,
    get_chains_by_level,
    get_units_by_level,
)


@pytest.mark.asyncio
async def test_get_all_units():
    db = MockSession()
    unit = SimpleNamespace(id=uuid.uuid4(), name_de="ADC")
    db.queue_execute([unit])

    result = await get_all_units(db)
    assert result == [unit]


@pytest.mark.asyncio
async def test_get_units_by_level():
    db = MockSession()
    level_id = uuid.uuid4()
    unit = SimpleNamespace(id=uuid.uuid4(), level_id=level_id, name_de="DAC")
    db.queue_execute([unit])

    result = await get_units_by_level(db, level_id)
    assert result == [unit]


@pytest.mark.asyncio
async def test_get_chains_by_level_empty():
    db = MockSession()
    db.queue_execute([])

    result = await get_chains_by_level(db, uuid.uuid4())
    assert result == []


@pytest.mark.asyncio
async def test_get_chains_by_level_with_chain():
    db = MockSession()
    level_id = uuid.uuid4()
    unit_id = uuid.uuid4()
    link = SimpleNamespace(position=1, tech_unit_id=unit_id)
    chain = SimpleNamespace(
        id=uuid.uuid4(),
        name="Signal Chain",
        level_id=level_id,
        description="Test chain",
        links=[link],
    )
    unit = SimpleNamespace(id=unit_id, name_de="Sensor")
    db.queue_execute([chain])
    db.queue_get(unit)  # db.get(TechUnit, unit_id)

    result = await get_chains_by_level(db, level_id)
    assert len(result) == 1
    assert result[0]["name"] == "Signal Chain"
    assert len(result[0]["units"]) == 1


# ── L03 Subjects & Modules ───────────────────────────────────────────


from app.layers.L03_subjects_modules.service import (
    get_all_modules,
    get_all_subjects,
    get_module_detail,
    get_modules_by_subject,
)


@pytest.mark.asyncio
async def test_get_all_subjects():
    db = MockSession()
    subj = SimpleNamespace(id=uuid.uuid4(), name_de="Anatomie")
    db.queue_execute([subj])

    result = await get_all_subjects(db)
    assert result == [subj]


@pytest.mark.asyncio
async def test_get_modules_by_subject():
    db = MockSession()
    subject_id = uuid.uuid4()
    mod = SimpleNamespace(id=uuid.uuid4(), subject_id=subject_id, code="AP-101")
    db.queue_execute([mod])

    result = await get_modules_by_subject(db, subject_id)
    assert result == [mod]


@pytest.mark.asyncio
async def test_get_module_detail_found():
    db = MockSession()
    mod = SimpleNamespace(id=uuid.uuid4(), name_de="Anatomie I", units=[])
    db.queue_execute(mod)

    result = await get_module_detail(db, mod.id)
    assert result.name_de == "Anatomie I"


@pytest.mark.asyncio
async def test_get_module_detail_not_found():
    db = MockSession()
    db.queue_execute(None)

    with pytest.raises(NotFoundError):
        await get_module_detail(db, uuid.uuid4())


@pytest.mark.asyncio
async def test_get_all_modules_no_filter():
    db = MockSession()
    mod1 = SimpleNamespace(semester=1, code="AP-101")
    mod2 = SimpleNamespace(semester=2, code="AP-201")
    db.queue_execute([mod1, mod2])

    result = await get_all_modules(db)
    assert result == [mod1, mod2]


@pytest.mark.asyncio
async def test_get_all_modules_with_semester():
    db = MockSession()
    mod = SimpleNamespace(semester=1, code="AP-101")
    db.queue_execute([mod])

    result = await get_all_modules(db, semester=1)
    assert result == [mod]


# ── L04 Content & Eselsbrücken ────────────────────────────────────────


from app.layers.L04_content_eselsbruecken.models import MnemonicType
from app.layers.L04_content_eselsbruecken.service import (
    get_content_for_unit,
    get_content_with_body,
    get_mnemonics_for_content,
)


@pytest.mark.asyncio
async def test_get_content_for_unit_found():
    db = MockSession()
    content = SimpleNamespace(id=uuid.uuid4(), module_unit_id=uuid.uuid4())
    db.queue_execute(content)

    result = await get_content_for_unit(db, content.module_unit_id)
    assert result.id == content.id


@pytest.mark.asyncio
async def test_get_content_for_unit_not_found():
    db = MockSession()
    db.queue_execute(None)

    with pytest.raises(NotFoundError):
        await get_content_for_unit(db, uuid.uuid4())


@pytest.mark.asyncio
async def test_get_content_with_body_no_version():
    db = MockSession()
    content = SimpleNamespace(id=uuid.uuid4(), module_unit_id=uuid.uuid4(), current_version_id=None)
    db.queue_execute(content)

    result_content, body = await get_content_with_body(db, content.module_unit_id)
    assert body == ""
    assert result_content.id == content.id


@pytest.mark.asyncio
async def test_get_content_with_body_with_version():
    db = MockSession()
    version_id = uuid.uuid4()
    content = SimpleNamespace(id=uuid.uuid4(), module_unit_id=uuid.uuid4(), current_version_id=version_id)
    version = SimpleNamespace(id=version_id, body_markdown="# Zelle\nAufbau und Funktion.")
    db.queue_execute(content)
    db.queue_execute(version)

    _, body = await get_content_with_body(db, content.module_unit_id)
    assert body == "# Zelle\nAufbau und Funktion."


@pytest.mark.asyncio
async def test_get_mnemonics_for_content():
    db = MockSession()
    content_id = uuid.uuid4()
    mnemonic = SimpleNamespace(id=uuid.uuid4(), content_id=content_id, mnemonic_type=MnemonicType.ACRONYM)
    db.queue_execute([mnemonic])

    result = await get_mnemonics_for_content(db, content_id)
    assert result == [mnemonic]


@pytest.mark.asyncio
async def test_get_mnemonics_for_content_with_user():
    db = MockSession()
    content_id = uuid.uuid4()
    user_id = uuid.uuid4()
    mnemonic = SimpleNamespace(id=uuid.uuid4(), content_id=content_id)
    db.queue_execute([mnemonic])

    result = await get_mnemonics_for_content(db, content_id, user_id=user_id)
    assert result == [mnemonic]


# ── L05 Knowledge Assessment ──────────────────────────────────────────


from app.layers.L05_knowledge_assessment.models import QuestionType
from app.layers.L05_knowledge_assessment.service import (
    get_exams_by_module,
    start_exam,
    submit_exam,
)


@pytest.mark.asyncio
async def test_get_exams_by_module():
    db = MockSession()
    exam = SimpleNamespace(id=uuid.uuid4(), module_id=uuid.uuid4())
    db.queue_execute([exam])

    result = await get_exams_by_module(db, exam.module_id)
    assert result == [exam]


@pytest.mark.asyncio
async def test_start_exam_not_found():
    db = MockSession()
    db.queue_get(None)  # exam not found

    with pytest.raises(NotFoundError):
        await start_exam(db, uuid.uuid4(), uuid.uuid4())


@pytest.mark.asyncio
async def test_start_exam_success():
    from app.core.events import EventBus

    EventBus.clear()

    db = MockSession()
    exam_id = uuid.uuid4()
    exam = SimpleNamespace(id=exam_id, module_id=uuid.uuid4())
    db.queue_get(exam)  # db.get(Exam, exam_id)

    attempt = SimpleNamespace(id=uuid.uuid4(), exam_id=exam_id, user_id=uuid.uuid4())

    # Queue execute results: ExamQuestion list, then QuestionBank list
    eq = SimpleNamespace(exam_id=exam_id, question_id=uuid.uuid4(), position=1)
    question = SimpleNamespace(id=eq.question_id, question_de="Was ist EKG?")

    db.queue_execute([eq])      # select ExamQuestion
    db.queue_execute([question])  # select QuestionBank

    with patch("app.layers.L05_knowledge_assessment.service.ExamAttempt") as MockAttempt:
        mock_attempt = SimpleNamespace(
            id=uuid.uuid4(), exam_id=exam_id, user_id=uuid.uuid4(),
            total_score=None, passed=None
        )
        MockAttempt.return_value = mock_attempt

        result_attempt, questions = await start_exam(db, exam_id, uuid.uuid4())
        assert result_attempt is mock_attempt
        assert len(questions) == 1


@pytest.mark.asyncio
async def test_submit_exam_not_found():
    db = MockSession()
    db.queue_get(None)  # attempt not found

    with pytest.raises(NotFoundError):
        await submit_exam(db, uuid.uuid4(), [])


@pytest.mark.asyncio
async def test_submit_exam_multiple_choice_correct():
    from app.core.events import EventBus

    EventBus.clear()

    db = MockSession()
    question_id = uuid.uuid4()
    attempt = SimpleNamespace(
        id=uuid.uuid4(), exam_id=uuid.uuid4(), user_id=uuid.uuid4(),
        total_score=None, passed=None
    )
    question = SimpleNamespace(
        id=question_id,
        question_type=QuestionType.MULTIPLE_CHOICE,
        correct_answer={"answer": "A"},
    )
    db.queue_get(attempt)     # get(ExamAttempt, attempt_id)
    db.queue_get(question)    # get(QuestionBank, question_id)

    answers = [{"question_id": question_id, "answer_data": {"answer": "A"}}]

    with patch("app.layers.L05_knowledge_assessment.service.EventBus.publish", new_callable=AsyncMock):
        result = await submit_exam(db, attempt.id, answers)
        assert result.total_score == 100.0
        assert result.passed is True


@pytest.mark.asyncio
async def test_submit_exam_multiple_choice_wrong():
    from app.core.events import EventBus

    EventBus.clear()

    db = MockSession()
    question_id = uuid.uuid4()
    attempt = SimpleNamespace(
        id=uuid.uuid4(), exam_id=uuid.uuid4(), user_id=uuid.uuid4(),
        total_score=None, passed=None
    )
    question = SimpleNamespace(
        id=question_id,
        question_type=QuestionType.MULTIPLE_CHOICE,
        correct_answer={"answer": "A"},
    )
    db.queue_get(attempt)
    db.queue_get(question)

    answers = [{"question_id": question_id, "answer_data": {"answer": "B"}}]

    with patch("app.layers.L05_knowledge_assessment.service.EventBus.publish", new_callable=AsyncMock):
        result = await submit_exam(db, attempt.id, answers)
        assert result.total_score == 0.0
        assert result.passed is False


# ── L06 Project Creation ──────────────────────────────────────────────


from app.layers.L06_project_creation.schemas import (
    MilestoneCreate,
    MilestoneUpdate,
    ProjectCreate,
    ProjectUpdate,
)
from app.layers.L06_project_creation.service import (
    add_artifact,
    add_milestone,
    create_project,
    get_project,
    get_user_projects,
    update_project,
)
from app.shared.exceptions import ForbiddenError


@pytest.mark.asyncio
async def test_create_project():
    db = MockSession()
    user_id = uuid.uuid4()
    data = ProjectCreate(title="EKG-Sensor", description="Cardiac monitor")

    result = await create_project(db, data, user_id)
    assert len(db.added) == 1
    assert db.flushed


@pytest.mark.asyncio
async def test_get_user_projects():
    db = MockSession()
    user_id = uuid.uuid4()
    project = SimpleNamespace(id=uuid.uuid4(), created_by=user_id, title="EKG")
    db.queue_execute([project])

    result = await get_user_projects(db, user_id)
    assert result == [project]


@pytest.mark.asyncio
async def test_get_project_not_found():
    db = MockSession()
    db.queue_execute(None)  # scalar_one_or_none returns None

    with pytest.raises(NotFoundError):
        await get_project(db, uuid.uuid4())


@pytest.mark.asyncio
async def test_get_project_forbidden():
    db = MockSession()
    owner_id = uuid.uuid4()
    other_id = uuid.uuid4()
    project = SimpleNamespace(id=uuid.uuid4(), created_by=owner_id, milestones=[], artifacts=[])
    db.queue_execute(project)

    with pytest.raises(ForbiddenError):
        await get_project(db, project.id, user_id=other_id)


@pytest.mark.asyncio
async def test_get_project_success():
    db = MockSession()
    user_id = uuid.uuid4()
    project = SimpleNamespace(id=uuid.uuid4(), created_by=user_id, milestones=[], artifacts=[])
    db.queue_execute(project)

    result = await get_project(db, project.id, user_id=user_id)
    assert result.created_by == user_id


@pytest.mark.asyncio
async def test_update_project():
    db = MockSession()
    user_id = uuid.uuid4()
    project = SimpleNamespace(
        id=uuid.uuid4(), created_by=user_id, title="Old", description="", milestones=[], artifacts=[],
        status=None, realization_stage=None
    )
    db.queue_execute(project)

    data = ProjectUpdate(title="New Title")
    result = await update_project(db, project.id, data, user_id)
    assert result.title == "New Title"


@pytest.mark.asyncio
async def test_add_milestone():
    db = MockSession()
    user_id = uuid.uuid4()
    project_id = uuid.uuid4()
    project = SimpleNamespace(id=project_id, created_by=user_id, milestones=[], artifacts=[])

    # get_project does db.execute → returns project
    db.queue_execute(project)
    # count query returns 0
    db.queue_execute(0)

    data = MilestoneCreate(title="MVP complete", description="")
    result = await add_milestone(db, project_id, data, user_id)
    assert db.flushed
    milestone_added = db.added[-1]
    assert milestone_added.title == "MVP complete"
    assert milestone_added.position == 1


@pytest.mark.asyncio
async def test_add_artifact():
    db = MockSession()
    user_id = uuid.uuid4()
    project_id = uuid.uuid4()
    project = SimpleNamespace(id=project_id, created_by=user_id, milestones=[], artifacts=[])
    db.queue_execute(project)

    result = await add_artifact(db, project_id, "https://example.com/file.pdf", "pdf", user_id)
    assert db.flushed
    artifact = db.added[-1]
    assert artifact.file_url == "https://example.com/file.pdf"


# ── L07 Faculty Collaboration ─────────────────────────────────────────


from app.layers.L07_faculty_collaboration.schemas import (
    FacultyProfileCreate,
    FacultyProfileUpdate,
)
from app.layers.L07_faculty_collaboration.service import (
    accept_review,
    complete_review,
    create_faculty_profile,
    decline_review,
    get_available_faculty,
    get_faculty_profile,
    update_faculty_profile,
)
from app.shared.exceptions import ConflictError


@pytest.mark.asyncio
async def test_get_available_faculty():
    db = MockSession()
    faculty = SimpleNamespace(id=uuid.uuid4(), available_for_review=True)
    db.queue_execute([faculty])

    result = await get_available_faculty(db)
    assert result == [faculty]


@pytest.mark.asyncio
async def test_get_faculty_profile_found():
    db = MockSession()
    user_id = uuid.uuid4()
    profile = SimpleNamespace(id=uuid.uuid4(), user_id=user_id)
    db.queue_execute(profile)

    result = await get_faculty_profile(db, user_id)
    assert result.user_id == user_id


@pytest.mark.asyncio
async def test_create_faculty_profile_conflict():
    db = MockSession()
    user_id = uuid.uuid4()
    existing = SimpleNamespace(id=uuid.uuid4(), user_id=user_id)
    db.queue_execute(existing)  # get_faculty_profile returns existing

    data = FacultyProfileCreate(department="Medizintechnik", expertise_areas=["EKG"])
    with pytest.raises(ConflictError):
        await create_faculty_profile(db, user_id, data)


@pytest.mark.asyncio
async def test_create_faculty_profile_success():
    db = MockSession()
    user_id = uuid.uuid4()
    db.queue_execute(None)  # no existing profile

    data = FacultyProfileCreate(department="Medizintechnik", expertise_areas=["EKG", "Biosignals"])
    result = await create_faculty_profile(db, user_id, data)
    assert len(db.added) == 1
    assert db.added[0].department == "Medizintechnik"


@pytest.mark.asyncio
async def test_update_faculty_profile_not_found():
    db = MockSession()
    db.queue_execute(None)

    data = FacultyProfileUpdate(department="New Dept")
    with pytest.raises(NotFoundError):
        await update_faculty_profile(db, uuid.uuid4(), data)


@pytest.mark.asyncio
async def test_update_faculty_profile_success():
    db = MockSession()
    user_id = uuid.uuid4()
    profile = SimpleNamespace(
        id=uuid.uuid4(), user_id=user_id,
        department="Old", expertise_areas={"areas": []}, available_for_review=False
    )
    db.queue_execute(profile)

    data = FacultyProfileUpdate(department="New Dept", available_for_review=True)
    result = await update_faculty_profile(db, user_id, data)
    assert result.department == "New Dept"
    assert result.available_for_review is True


@pytest.mark.asyncio
async def test_accept_review_success():
    db = MockSession()
    faculty_id = uuid.uuid4()
    faculty_user_id = uuid.uuid4()
    review = SimpleNamespace(
        id=uuid.uuid4(), faculty_id=faculty_id, status=None
    )
    profile = SimpleNamespace(id=faculty_id, user_id=faculty_user_id)
    db.queue_get(review)
    db.queue_execute(profile)  # get_faculty_profile → execute

    result = await accept_review(db, review.id, faculty_user_id)
    assert result.status.value == "accepted"


@pytest.mark.asyncio
async def test_decline_review_success():
    db = MockSession()
    faculty_id = uuid.uuid4()
    faculty_user_id = uuid.uuid4()
    review = SimpleNamespace(id=uuid.uuid4(), faculty_id=faculty_id, status=None)
    profile = SimpleNamespace(id=faculty_id, user_id=faculty_user_id)
    db.queue_get(review)
    db.queue_execute(profile)

    result = await decline_review(db, review.id, faculty_user_id)
    assert result.status.value == "declined"


@pytest.mark.asyncio
async def test_complete_review_forbidden():
    db = MockSession()
    review = SimpleNamespace(id=uuid.uuid4(), faculty_id=uuid.uuid4(), status=None)
    other_profile = SimpleNamespace(id=uuid.uuid4())
    db.queue_get(review)
    db.queue_execute(other_profile)

    with pytest.raises(ForbiddenError):
        await complete_review(db, review.id, "Great work!", uuid.uuid4())


# ── L08 Product Frontend Preferences ─────────────────────────────────


from app.layers.L08_product_frontend.schemas import UserPreferenceUpdate
from app.layers.L08_product_frontend.service import get_preferences, update_preferences


@pytest.mark.asyncio
async def test_get_preferences_existing():
    db = MockSession()
    user_id = uuid.uuid4()
    prefs = SimpleNamespace(user_id=user_id, theme="dark")
    db.queue_execute(prefs)

    result = await get_preferences(db, user_id)
    assert result.theme == "dark"


@pytest.mark.asyncio
async def test_get_preferences_creates_default():
    db = MockSession()
    user_id = uuid.uuid4()
    db.queue_execute(None)  # no existing prefs → service creates a new record

    result = await get_preferences(db, user_id)
    assert len(db.added) == 1
    assert db.flushed


@pytest.mark.asyncio
async def test_update_preferences():
    db = MockSession()
    user_id = uuid.uuid4()
    prefs = SimpleNamespace(user_id=user_id, theme="light", high_contrast=False)
    db.queue_execute(prefs)  # for get_preferences

    data = UserPreferenceUpdate(theme="dark")
    result = await update_preferences(db, user_id, data)
    assert result.theme == "dark"


# ── L09 Dimensional Realization ───────────────────────────────────────


from app.layers.L09_dimensional_realization.models import RealizationStage
from app.layers.L09_dimensional_realization.schemas import AdvanceStageRequest
from app.layers.L09_dimensional_realization.service import (
    advance_stage,
    get_criteria_for_stage,
    list_criteria,
)


@pytest.mark.asyncio
async def test_list_criteria():
    db = MockSession()
    criterion = SimpleNamespace(id=uuid.uuid4(), stage=RealizationStage.IDEA)
    db.queue_execute([criterion])

    result = await list_criteria(db)
    assert result == [criterion]


@pytest.mark.asyncio
async def test_get_criteria_for_stage_found():
    db = MockSession()
    criterion = SimpleNamespace(stage=RealizationStage.MVP)
    db.queue_execute(criterion)

    result = await get_criteria_for_stage(db, RealizationStage.MVP)
    assert result.stage == RealizationStage.MVP


@pytest.mark.asyncio
async def test_get_criteria_for_stage_not_found():
    db = MockSession()
    db.queue_execute(None)

    with pytest.raises(NotFoundError):
        await get_criteria_for_stage(db, RealizationStage.CONCEPT)


@pytest.mark.asyncio
async def test_advance_stage():
    db = MockSession()
    user_id = uuid.uuid4()
    project_id = uuid.uuid4()
    data = AdvanceStageRequest(
        project_id=project_id,
        target_stage=RealizationStage.MVP,
        evidence="MVP milestone completed",
    )

    with patch("app.layers.L09_dimensional_realization.service.ProjectRealization") as MockReal:
        mock_real = SimpleNamespace(id=uuid.uuid4(), project_id=project_id, stage=RealizationStage.MVP)
        MockReal.return_value = mock_real
        result = await advance_stage(db, data, user_id)
        assert result.stage == RealizationStage.MVP
        assert db.flushed


# ── L10 I/O Definition ────────────────────────────────────────────────


from app.layers.L10_io_definition.schemas import UserIOPreferenceUpdate
from app.layers.L10_io_definition.service import (
    get_user_io_preferences,
    list_capabilities,
    update_user_io_preferences,
)


@pytest.mark.asyncio
async def test_list_capabilities():
    db = MockSession()
    cap = SimpleNamespace(id=uuid.uuid4(), name="VOICE", type="voice", enabled=True)
    db.queue_execute([cap])

    result = await list_capabilities(db)
    assert result == [cap]


@pytest.mark.asyncio
async def test_get_user_io_preferences_existing():
    db = MockSession()
    user_id = uuid.uuid4()
    prefs = SimpleNamespace(user_id=user_id, input_mode="text")
    db.queue_execute(prefs)

    result = await get_user_io_preferences(db, user_id)
    assert result.input_mode == "text"


@pytest.mark.asyncio
async def test_get_user_io_preferences_creates_default():
    db = MockSession()
    user_id = uuid.uuid4()
    db.queue_execute(None)  # no existing prefs → service creates a new record

    await get_user_io_preferences(db, user_id)
    assert len(db.added) == 1
    assert db.flushed


@pytest.mark.asyncio
async def test_update_user_io_preferences():
    db = MockSession()
    user_id = uuid.uuid4()
    prefs = SimpleNamespace(user_id=user_id, input_mode="text", output_mode="visual")
    db.queue_execute(prefs)

    data = UserIOPreferenceUpdate(input_mode="voice")
    result = await update_user_io_preferences(db, user_id, data)
    assert result.input_mode == "voice"


# ── L11 Legal Compliance ──────────────────────────────────────────────


from app.layers.L11_legal_compliance.schemas import (
    ComplianceEvidenceCreate,
    ComplianceStatusResponse,
)
from app.layers.L11_legal_compliance.service import (
    create_evidence,
    get_compliance_status,
    list_requirements,
)


@pytest.mark.asyncio
async def test_list_requirements_no_filter():
    db = MockSession()
    req = SimpleNamespace(id=uuid.uuid4(), framework="IEC 62304", clause="5.1")
    db.queue_execute([req])

    result = await list_requirements(db)
    assert result == [req]


@pytest.mark.asyncio
async def test_list_requirements_with_framework():
    db = MockSession()
    req = SimpleNamespace(id=uuid.uuid4(), framework="MDR", clause="Art. 10")
    db.queue_execute([req])

    result = await list_requirements(db, framework="MDR")
    assert result == [req]


@pytest.mark.asyncio
async def test_get_compliance_status():
    db = MockSession()
    db.queue_execute(5)  # total requirements
    db.queue_execute(3)  # evidenced
    db.queue_execute(2)  # verified

    result = await get_compliance_status(db)
    assert result.total_requirements == 5
    assert result.evidenced_requirements == 3
    assert result.verified_requirements == 2
    assert result.compliance_percentage == 60.0


@pytest.mark.asyncio
async def test_get_compliance_status_no_requirements():
    db = MockSession()
    db.queue_execute(0)
    db.queue_execute(0)
    db.queue_execute(0)

    result = await get_compliance_status(db)
    assert result.compliance_percentage == 0.0


@pytest.mark.asyncio
async def test_create_evidence():
    db = MockSession()
    user_id = uuid.uuid4()
    req_id = uuid.uuid4()
    data = ComplianceEvidenceCreate(
        requirement_id=req_id,
        evidence_type="document",
        description="Test evidence",
    )

    result = await create_evidence(db, data, user_id)
    assert len(db.added) == 1
    assert db.added[0].requirement_id == req_id
    assert db.flushed


# ── L12 Quality Management ────────────────────────────────────────────


from app.layers.L12_quality_management.schemas import UserFeedbackCreate
from app.layers.L12_quality_management.service import (
    create_feedback,
    get_dashboard,
    list_metrics,
)


@pytest.mark.asyncio
async def test_list_metrics():
    db = MockSession()
    metric = SimpleNamespace(id=uuid.uuid4(), name="Test Coverage", target_value=80.0, unit="%")
    db.queue_execute([metric])

    result = await list_metrics(db)
    assert result == [metric]


@pytest.mark.asyncio
async def test_get_dashboard():
    db = MockSession()
    metric_id = uuid.uuid4()
    metric = SimpleNamespace(id=metric_id, name="Coverage", target_value=80.0, unit="%")
    db.queue_execute([metric])    # list_metrics
    db.queue_execute(79.5)        # latest measurement
    db.queue_execute(10)          # feedback count
    db.queue_execute(4.2)         # avg rating

    result = await get_dashboard(db)
    assert result.total_feedback_count == 10
    assert result.average_rating == 4.2
    assert len(result.metrics) == 1
    assert result.metrics[0].latest_value == 79.5


@pytest.mark.asyncio
async def test_get_dashboard_no_metrics():
    db = MockSession()
    db.queue_execute([])   # no metrics
    db.queue_execute(0)    # feedback count
    db.queue_execute(None) # avg rating None

    result = await get_dashboard(db)
    assert result.total_feedback_count == 0
    assert result.average_rating is None


@pytest.mark.asyncio
async def test_create_feedback():
    db = MockSession()
    user_id = uuid.uuid4()
    data = UserFeedbackCreate(category="bug", text="Something is wrong", rating=2)

    result = await create_feedback(db, data, user_id)
    assert db.flushed
    feedback = db.added[-1]
    assert feedback.category == "bug"
    assert feedback.rating == 2


# ── L13 Social & Engineering Impact ──────────────────────────────────


from app.layers.L13_social_engineering_impact.schemas import SurveyResponseCreate
from app.layers.L13_social_engineering_impact.service import (
    list_assessments,
    list_surveys,
    submit_survey_response,
)


@pytest.mark.asyncio
async def test_list_assessments():
    db = MockSession()
    assessment = SimpleNamespace(id=uuid.uuid4(), title="Privacy Risk", risk_level="high")
    db.queue_execute([assessment])

    result = await list_assessments(db)
    assert result == [assessment]


@pytest.mark.asyncio
async def test_list_surveys():
    db = MockSession()
    survey = SimpleNamespace(id=uuid.uuid4(), title="User Satisfaction")
    db.queue_execute([survey])

    result = await list_surveys(db)
    assert result == [survey]


@pytest.mark.asyncio
async def test_submit_survey_response_not_found():
    db = MockSession()
    db.queue_get(None)  # survey not found

    data = SurveyResponseCreate(survey_id=uuid.uuid4(), responses={"q1": "yes"})
    with pytest.raises(NotFoundError):
        await submit_survey_response(db, data, uuid.uuid4())


@pytest.mark.asyncio
async def test_submit_survey_response_success():
    db = MockSession()
    user_id = uuid.uuid4()
    survey_id = uuid.uuid4()
    survey = SimpleNamespace(id=survey_id, title="Satisfaction Survey")
    db.queue_get(survey)

    data = SurveyResponseCreate(survey_id=survey_id, responses={"q1": "strongly_agree"})

    with patch("app.layers.L13_social_engineering_impact.service.SurveyResponseModel") as MockResp:
        mock_resp = SimpleNamespace(id=uuid.uuid4(), survey_id=survey_id, user_id=user_id)
        MockResp.return_value = mock_resp
        result = await submit_survey_response(db, data, user_id)
        assert result.survey_id == survey_id
        assert db.flushed


# ── ProjectAnalyzer (offline / fallback) ─────────────────────────────


from app.services.project_analyzer import ProjectAnalyzer


def test_analyzer_offline_level_b_ekg():
    analyzer = ProjectAnalyzer()
    result = analyzer.analyze_project_idea_offline("EKG-Wearable für Sportler")
    assert result.complexity_level == "B"
    assert result.complexity_name_de  # non-empty
    assert len(result.required_modules) > 0
    assert len(result.suggested_milestones) > 0


def test_analyzer_offline_level_a_default():
    analyzer = ProjectAnalyzer()
    result = analyzer.analyze_project_idea_offline("Ein einfaches Gerät")
    assert result.complexity_level == "A"
    assert result.reasoning != ""


def test_analyzer_offline_level_c_app():
    analyzer = ProjectAnalyzer()
    result = analyzer.analyze_project_idea_offline("Diagnose-App für Telemedizin")
    assert result.complexity_level == "C"


def test_analyzer_offline_level_d_implant():
    analyzer = ProjectAnalyzer()
    result = analyzer.analyze_project_idea_offline("Implantierbarer Neurostimulator")
    assert result.complexity_level == "D"


def test_analyzer_offline_level_e_mrt():
    analyzer = ProjectAnalyzer()
    result = analyzer.analyze_project_idea_offline("MRT-Zubehör für offene Systeme")
    assert result.complexity_level == "E"


def test_analyzer_offline_learning_path_phases():
    analyzer = ProjectAnalyzer()
    result = analyzer.analyze_project_idea_offline("EKG-Monitor für Notaufnahme")
    # Learning path phases must cover modules
    assert isinstance(result.learning_path, list)
    total_modules_in_phases = sum(len(p.modules) for p in result.learning_path)
    assert total_modules_in_phases == len(result.required_modules)


def test_analyzer_build_module_catalog():
    analyzer = ProjectAnalyzer()
    catalog = analyzer._build_module_catalog()
    assert "AP-101" in catalog or len(catalog) > 0  # non-empty catalog


def test_analyzer_build_analysis_from_dict():
    analyzer = ProjectAnalyzer()
    raw = {
        "complexity_level": "B",
        "reasoning": "EKG erfordert Signalverarbeitung",
        "additional_modules": [],
        "project_context": {"AP-101": "Wichtig für Physiologie"},
        "suggested_milestones": [{"title": "MVP", "description": "Erster Prototyp"}],
        "learning_phases": [
            {
                "phase_number": 1,
                "title_de": "Phase 1: Grundlagen",
                "title_en": "Phase 1: Basics",
                "semester_equivalent": 1,
                "module_codes": ["AP-101"],
                "project_relevance": "Grundlagen der Anatomie",
            }
        ],
    }
    result = analyzer._build_analysis(raw)
    assert result.complexity_level == "B"
    assert result.reasoning == "EKG erfordert Signalverarbeitung"
    assert len(result.suggested_milestones) == 1


@pytest.mark.asyncio
async def test_analyzer_analyze_project_idea_with_ai():
    analyzer = ProjectAnalyzer()
    mock_client = AsyncMock()
    raw_json = """{
        "complexity_level": "B",
        "reasoning": "EKG Wearable requires biosignal processing",
        "additional_modules": [],
        "project_context": {},
        "suggested_milestones": [{"title": "Prototyp", "description": "Erster Hardware-Prototyp"}],
        "learning_phases": []
    }"""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=raw_json)]
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    analyzer.client = mock_client

    result = await analyzer.analyze_project_idea("EKG Wearable für Sportler")
    assert result.complexity_level == "B"
    assert len(result.suggested_milestones) == 1


# ── i18n utilities ────────────────────────────────────────────────────


from app.core.i18n import Locale, localized_field


def test_locale_enum_values():
    assert Locale.DE.value == "de"
    assert Locale.EN.value == "en"


def test_localized_field_de():
    obj = SimpleNamespace(name_de="Anatomie", name_en="Anatomy")
    result = localized_field(obj, "name", Locale.DE)
    assert result == "Anatomie"


def test_localized_field_en():
    obj = SimpleNamespace(name_de="Anatomie", name_en="Anatomy")
    result = localized_field(obj, "name", Locale.EN)
    assert result == "Anatomy"


def test_localized_field_fallback_to_de():
    # EN field is empty → fall back to DE
    obj = SimpleNamespace(name_de="Anatomie", name_en="")
    result = localized_field(obj, "name", Locale.EN)
    assert result == "Anatomie"


def test_localized_field_missing_returns_empty():
    obj = SimpleNamespace()
    result = localized_field(obj, "name", Locale.DE)
    assert result == ""


# ── L11 Compliance Template Integrity ────────────────────────────────


from app.layers.L11_legal_compliance.templates import (
    ALL_TEMPLATES,
    GDPR_TEMPLATES,
    IEC_62304_TEMPLATES,
    IEC_62366_TEMPLATES,
    ISO_10993_TEMPLATES,
    ISO_13485_TEMPLATES,
    ISO_14971_TEMPLATES,
    MDR_TEMPLATES,
)


def test_all_templates_non_empty():
    assert len(ALL_TEMPLATES) > 0


def test_all_templates_covers_major_frameworks():
    frameworks = {t["framework"] for t in ALL_TEMPLATES}
    assert any("MDR" in f for f in frameworks)
    assert any("ISO 13485" in f for f in frameworks)
    assert any("ISO 14971" in f for f in frameworks)
    assert any("62304" in f for f in frameworks)
    assert any("GDPR" in f or "DSGVO" in f for f in frameworks)


def test_all_templates_required_fields():
    for template in ALL_TEMPLATES:
        assert "framework" in template, f"Missing 'framework': {template}"
        assert "clause" in template, f"Missing 'clause': {template}"
        assert "title" in template, f"Missing 'title': {template}"
        assert template["framework"], "framework must be non-empty"
        assert template["clause"], "clause must be non-empty"
        assert template["title"], "title must be non-empty"


def test_all_templates_aggregate_counts():
    expected_total = (
        len(MDR_TEMPLATES)
        + len(ISO_13485_TEMPLATES)
        + len(ISO_14971_TEMPLATES)
        + len(IEC_62304_TEMPLATES)
        + len(IEC_62366_TEMPLATES)
        + len(ISO_10993_TEMPLATES)
        + len(GDPR_TEMPLATES)
    )
    assert len(ALL_TEMPLATES) == expected_total


# ── L12 Quality Management Template Integrity ─────────────────────────


from app.layers.L12_quality_management.templates import SOFTWARE_COMPLIANCE_TEMPLATES


def test_software_compliance_templates_non_empty():
    assert len(SOFTWARE_COMPLIANCE_TEMPLATES) > 0


def test_software_compliance_templates_required_fields():
    for template in SOFTWARE_COMPLIANCE_TEMPLATES:
        assert "framework" in template, f"Missing 'framework': {template}"
        assert "clause" in template, f"Missing 'clause': {template}"
        assert "title" in template, f"Missing 'title': {template}"


def test_software_compliance_templates_known_frameworks():
    frameworks = {t["framework"] for t in SOFTWARE_COMPLIANCE_TEMPLATES}
    # Must contain IEC 62304 and IEC 62366 entries
    assert any("62304" in f for f in frameworks)
    assert any("62366" in f for f in frameworks)


# ── Seed Data Integrity ───────────────────────────────────────────────


from app.data.engineering_question_data import QUESTION_DATA
from app.data.engineering_content_data import CONTENT_DATA
from app.data.curriculum_data import MODULES, SUBJECTS


def test_question_data_non_empty():
    assert len(QUESTION_DATA) >= 10, "Expected at least 10 questions in seed data"


def test_question_data_required_fields():
    required = {"module_code", "question_text", "question_type", "options", "correct_answer"}
    for q in QUESTION_DATA:
        # QUESTION_DATA entries are plain dicts
        for field in required:
            assert field in q, f"Question missing field '{field}': {q}"


def test_content_data_non_empty():
    assert len(CONTENT_DATA) > 0, "CONTENT_DATA must have at least one module"


def test_content_data_has_markdown():
    for module_code, pages in CONTENT_DATA.items():
        assert len(pages) > 0, f"No pages for module {module_code}"
        first = pages[0]
        # Pages can be either plain strings or dicts with body_de / body key
        if isinstance(first, str):
            assert len(first) > 10, f"Page too short for {module_code}"
        elif isinstance(first, dict):
            body = first.get("body_de") or first.get("body") or ""
            assert len(body) > 10, f"body_de/body too short for {module_code}"
        else:
            raise AssertionError(f"Unexpected page type for {module_code}: {type(first)}")


def test_curriculum_subjects_non_empty():
    assert len(SUBJECTS) > 0


def test_curriculum_modules_non_empty():
    assert len(MODULES) > 0


def test_curriculum_modules_have_valid_subject_refs():
    subject_codes = {s.code for s in SUBJECTS}
    for m in MODULES:
        assert m.subject_code in subject_codes, (
            f"Module {m.code} references unknown subject_code '{m.subject_code}'"
        )

