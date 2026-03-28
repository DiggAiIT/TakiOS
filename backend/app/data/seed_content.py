"""
Seed script: Populate the TakiOS database with Engineering Harnessing content.

Layers seeded: L02, L04, L05, L09, L11, L12, L13.

Prerequisite: seed_curriculum.py must have run first (L01 knowledge levels
and L03 subjects/modules/units already exist in the database).

Usage:
    cd backend
    python -m app.data.seed_content
"""

from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.shared.base_model import AuditBase  # noqa: F401 — triggers model registration

# Import ALL layer models so SQLAlchemy knows about them
from app.core.auth.models import User, UserRole  # noqa: F401
from app.layers.L01_level_selection.models import KnowledgeLevel  # noqa: F401
from app.layers.L02_tech_units.models import TechUnit, TechUnitChain, TechUnitChainLink
from app.layers.L03_subjects_modules.models import Module, ModuleUnit  # noqa: F401
from app.layers.L04_content_eselsbruecken.models import Content, ContentVersion, Mnemonic
from app.layers.L05_knowledge_assessment.models import QuestionBank, Exam, ExamQuestion
from app.layers.L09_dimensional_realization.models import StageGateCriteria, RealizationStage
from app.layers.L11_legal_compliance.models import ComplianceRequirement
from app.layers.L11_legal_compliance.templates import ALL_TEMPLATES
from app.layers.L12_quality_management.models import QualityMetric
from app.layers.L13_social_engineering_impact.models import ImpactAssessment, Survey

from app.core.auth.service import hash_password

from app.data.engineering_harnessing_data import (
    TECH_UNITS,
    TECH_CHAINS,
    STAGE_GATE_DATA,
    QUALITY_METRICS,
    IMPACT_ASSESSMENTS,
    SURVEYS,
    MNEMONIC_DATA,
)

# Content and questions come from separate files (created by other agents)
from app.data.engineering_content_data import CONTENT_DATA
from app.data.engineering_question_data import QUESTION_DATA


# ─────────────────────────────────────────────────────────────────────────────
# Helper: Admin user
# ─────────────────────────────────────────────────────────────────────────────

async def ensure_admin_user(db: AsyncSession) -> uuid.UUID:
    """Find existing admin@takios.de or create it. Returns the user's UUID."""
    result = await db.execute(
        select(User).where(User.email == "admin@takios.de")
    )
    existing = result.scalar_one_or_none()
    if existing:
        print("  ✓ Admin user exists: admin@takios.de")
        return existing.id

    admin = User(
        email="admin@takios.de",
        password_hash=hash_password("TakiOS-Admin-2025!"),
        full_name="TakiOS Admin",
        role=UserRole.ADMIN,
        locale="de",
        is_active=True,
    )
    db.add(admin)
    await db.flush()
    print("  + Admin user created: admin@takios.de")
    return admin.id


# ─────────────────────────────────────────────────────────────────────────────
# Helper: Fetch existing L01/L03 data
# ─────────────────────────────────────────────────────────────────────────────

async def get_level_ids(db: AsyncSession) -> dict[str, uuid.UUID]:
    """
    Query KnowledgeLevel.pyramid_position 1→"A", 2→"B", 3→"C", 4→"D", 5→"E".
    Returns {"A": uuid, "B": uuid, ...}.
    """
    result = await db.execute(select(KnowledgeLevel))
    levels = result.scalars().all()

    pos_to_letter = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
    level_ids: dict[str, uuid.UUID] = {}
    for lvl in levels:
        letter = pos_to_letter.get(lvl.pyramid_position)
        if letter:
            level_ids[letter] = lvl.id

    print(f"  Found {len(level_ids)} knowledge levels: {sorted(level_ids.keys())}")
    return level_ids


async def get_module_ids(db: AsyncSession) -> dict[str, uuid.UUID]:
    """
    Query all Module records. Returns {module_code: uuid}.
    """
    result = await db.execute(select(Module))
    modules = result.scalars().all()
    module_ids = {m.code: m.id for m in modules}
    print(f"  Found {len(module_ids)} modules")
    return module_ids


async def get_unit_ids(
    db: AsyncSession,
    module_ids: dict[str, uuid.UUID],
) -> dict[tuple[str, int], uuid.UUID]:
    """
    Query ModuleUnit by module_id + position (1-indexed in DB).
    Returns {(module_code, 0-indexed): uuid}.

    DB position 1 maps to dict key index 0.
    """
    result = await db.execute(select(ModuleUnit))
    units = result.scalars().all()

    # Build reverse map: module_id → code
    id_to_code = {v: k for k, v in module_ids.items()}

    unit_ids: dict[tuple[str, int], uuid.UUID] = {}
    for unit in units:
        code = id_to_code.get(unit.module_id)
        if code is not None:
            # Convert DB 1-indexed position → 0-indexed dict key
            unit_ids[(code, unit.position - 1)] = unit.id

    print(f"  Found {len(unit_ids)} module units")
    return unit_ids


# ─────────────────────────────────────────────────────────────────────────────
# L02 — Tech Units & Chains
# ─────────────────────────────────────────────────────────────────────────────

async def seed_tech_units(
    db: AsyncSession,
    level_ids: dict[str, uuid.UUID],
) -> dict[str, uuid.UUID]:
    """
    For each TechUnitDef in TECH_UNITS: check existence by name_en, insert if
    missing. Returns {name_en: id}.
    """
    tech_unit_ids: dict[str, uuid.UUID] = {}
    created = 0
    skipped = 0

    for tu in TECH_UNITS:
        result = await db.execute(
            select(TechUnit).where(TechUnit.name_en == tu.name_en)
        )
        existing = result.scalar_one_or_none()
        if existing:
            tech_unit_ids[tu.name_en] = existing.id
            skipped += 1
            continue

        level_id = level_ids.get(tu.level)
        if level_id is None:
            print(f"  ⚠ Level '{tu.level}' not found for TechUnit '{tu.name_en}' — skipping")
            continue

        unit = TechUnit(
            level_id=level_id,
            name_de=tu.name_de,
            name_en=tu.name_en,
            description_de=tu.description_de,
            description_en=tu.description_en,
            io_spec=tu.io_spec,
            limitations=tu.limitations,
        )
        db.add(unit)
        await db.flush()
        tech_unit_ids[tu.name_en] = unit.id
        created += 1

    print(f"  TechUnits: {created} created, {skipped} already existed")
    return tech_unit_ids


async def seed_tech_chains(
    db: AsyncSession,
    level_ids: dict[str, uuid.UUID],
    tech_unit_ids: dict[str, uuid.UUID],
) -> None:
    """
    For each TechChainDef: check existence by name, insert TechUnitChain.
    Then for each unit in chain.unit_names_en: insert TechUnitChainLink at
    position idx+1.
    """
    created = 0
    skipped = 0

    for chain_def in TECH_CHAINS:
        result = await db.execute(
            select(TechUnitChain).where(TechUnitChain.name == chain_def.name)
        )
        existing = result.scalar_one_or_none()
        if existing:
            skipped += 1
            continue

        level_id = level_ids.get(chain_def.level)
        if level_id is None:
            print(f"  ⚠ Level '{chain_def.level}' not found for chain '{chain_def.name}' — skipping")
            continue

        chain = TechUnitChain(
            name=chain_def.name,
            level_id=level_id,
            description=chain_def.description,
        )
        db.add(chain)
        await db.flush()

        for idx, unit_name_en in enumerate(chain_def.unit_names_en):
            unit_id = tech_unit_ids.get(unit_name_en)
            if unit_id is None:
                print(f"  ⚠ TechUnit '{unit_name_en}' not found for chain '{chain_def.name}' — skipping link")
                continue

            link = TechUnitChainLink(
                chain_id=chain.id,
                tech_unit_id=unit_id,
                position=idx + 1,
            )
            db.add(link)

        await db.flush()
        created += 1

    print(f"  TechChains: {created} created, {skipped} already existed")


# ─────────────────────────────────────────────────────────────────────────────
# L04 — Content & ContentVersions
# ─────────────────────────────────────────────────────────────────────────────

async def seed_content(
    db: AsyncSession,
    unit_ids: dict[tuple[str, int], uuid.UUID],
    admin_id: uuid.UUID,
) -> dict[tuple[str, int], uuid.UUID]:
    """
    For each module_code in CONTENT_DATA:
      for each (idx, markdown) in enumerate(pages):
        key = (module_code, idx)
        if unit_ids.get(key) is None: skip (module unit not found)
        check if Content already exists for module_unit_id
        if not: create Content → db.flush()
                create ContentVersion → db.flush()
                content.current_version_id = version.id
    Returns {(module_code, idx): content_id}.
    """
    content_ids: dict[tuple[str, int], uuid.UUID] = {}
    created = 0
    skipped = 0

    for module_code, pages in CONTENT_DATA.items():
        for idx, markdown in enumerate(pages):
            key = (module_code, idx)
            module_unit_id = unit_ids.get(key)
            if module_unit_id is None:
                # Module unit not found — skip silently
                continue

            # Check if Content already exists for this module unit
            result = await db.execute(
                select(Content).where(Content.module_unit_id == module_unit_id)
            )
            existing = result.scalar_one_or_none()
            if existing:
                content_ids[key] = existing.id
                skipped += 1
                continue

            # Create Content record
            content = Content(
                module_unit_id=module_unit_id,
                current_version_id=None,
            )
            db.add(content)
            await db.flush()

            # Create ContentVersion record
            version = ContentVersion(
                content_id=content.id,
                body_markdown=markdown,
                version_number=1,
                created_by=admin_id,
                change_reason="Initial seed",
            )
            db.add(version)
            await db.flush()

            # Back-fill current_version_id
            content.current_version_id = version.id
            await db.flush()

            content_ids[key] = content.id
            created += 1

    print(f"  Content: {created} created, {skipped} already existed")
    return content_ids


# ─────────────────────────────────────────────────────────────────────────────
# L04 — Mnemonics
# ─────────────────────────────────────────────────────────────────────────────

async def seed_mnemonics(
    db: AsyncSession,
    content_ids: dict[tuple[str, int], uuid.UUID],
    admin_id: uuid.UUID,
) -> None:
    """
    For each MnemonicDef in MNEMONIC_DATA:
      look up content_id via content_ids[(module_code, unit_position)]
      check if Mnemonic already exists for this content_id with same text[:50]
      if not: insert Mnemonic
    """
    created = 0
    skipped = 0
    missing_content = 0

    for m in MNEMONIC_DATA:
        key = (m.module_code, m.unit_position)
        content_id = content_ids.get(key)
        if content_id is None:
            missing_content += 1
            continue

        text_prefix = m.mnemonic_text[:50]
        result = await db.execute(
            select(Mnemonic).where(
                Mnemonic.content_id == content_id,
                Mnemonic.mnemonic_text.startswith(text_prefix),
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            skipped += 1
            continue

        mnemonic = Mnemonic(
            content_id=content_id,
            user_id=None,
            mnemonic_text=m.mnemonic_text,
            mnemonic_type=m.mnemonic_type,
            language=m.language,
            ai_generated=False,
        )
        db.add(mnemonic)
        created += 1

    await db.flush()
    print(f"  Mnemonics: {created} created, {skipped} already existed, {missing_content} skipped (content not found)")


# ─────────────────────────────────────────────────────────────────────────────
# L05 — Question Bank
# ─────────────────────────────────────────────────────────────────────────────

async def seed_questions(
    db: AsyncSession,
    unit_ids: dict[tuple[str, int], uuid.UUID],
) -> dict[str, list[uuid.UUID]]:
    """
    For each QuestionDef in QUESTION_DATA:
      look up module_unit_id via unit_ids[(module_code, unit_position)]
      check if QuestionBank already exists for this module_unit_id with same question_de[:80]
      if not: insert QuestionBank
    Returns {module_code: [question_ids]}.
    """
    question_map: dict[str, list[uuid.UUID]] = {}
    created = 0
    skipped = 0
    missing_unit = 0

    for q in QUESTION_DATA:
        key = (q.module_code, q.unit_position)
        module_unit_id = unit_ids.get(key)
        if module_unit_id is None:
            missing_unit += 1
            continue

        question_prefix = q.question_de[:80]
        result = await db.execute(
            select(QuestionBank).where(
                QuestionBank.module_unit_id == module_unit_id,
                QuestionBank.question_de.startswith(question_prefix),
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            question_map.setdefault(q.module_code, []).append(existing.id)
            skipped += 1
            continue

        question = QuestionBank(
            module_unit_id=module_unit_id,
            question_type=q.question_type,
            question_de=q.question_de,
            question_en=q.question_en,
            answer_options=q.answer_options,
            correct_answer=q.correct_answer,
            difficulty=q.difficulty,
            bloom_level=q.bloom_level,
        )
        db.add(question)
        await db.flush()
        question_map.setdefault(q.module_code, []).append(question.id)
        created += 1

    print(
        f"  Questions: {created} created, {skipped} already existed, "
        f"{missing_unit} skipped (unit not found)"
    )
    return question_map


# ─────────────────────────────────────────────────────────────────────────────
# L05 — Exams
# ─────────────────────────────────────────────────────────────────────────────

async def seed_exams(
    db: AsyncSession,
    admin_id: uuid.UUID,
    module_ids: dict[str, uuid.UUID],
    question_map: dict[str, list[uuid.UUID]],
) -> None:
    """
    For each module_code in module_ids:
      if module_code not in question_map or len == 0: skip
      check if Exam already exists for module_id with title "Modulprüfung {module_code}"
      if not: insert Exam + ExamQuestion rows
    """
    created = 0
    skipped = 0

    for module_code, module_id in module_ids.items():
        q_ids = question_map.get(module_code)
        if not q_ids:
            continue

        title = f"Modulprüfung {module_code}"
        result = await db.execute(
            select(Exam).where(
                Exam.module_id == module_id,
                Exam.title == title,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            skipped += 1
            continue

        exam = Exam(
            module_id=module_id,
            title=title,
            exam_type="digital",
            time_limit_minutes=30,
            created_by=admin_id,
        )
        db.add(exam)
        await db.flush()

        for idx, q_id in enumerate(q_ids):
            exam_question = ExamQuestion(
                exam_id=exam.id,
                question_id=q_id,
                position=idx + 1,
                points=1.0,
            )
            db.add(exam_question)

        await db.flush()
        created += 1

    print(f"  Exams: {created} created, {skipped} already existed")


# ─────────────────────────────────────────────────────────────────────────────
# L09 — Stage Gates
# ─────────────────────────────────────────────────────────────────────────────

async def seed_stage_gates(db: AsyncSession) -> None:
    """
    For each item in STAGE_GATE_DATA:
      check if StageGateCriteria already exists for that stage enum value
      if not: insert StageGateCriteria
    """
    created = 0
    skipped = 0

    for item in STAGE_GATE_DATA:
        stage_value = item["stage"]
        result = await db.execute(
            select(StageGateCriteria).where(
                StageGateCriteria.stage == stage_value
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            skipped += 1
            continue

        gate = StageGateCriteria(
            stage=stage_value,
            criteria=item["criteria"],
            required_artifacts=item["required_artifacts"],
        )
        db.add(gate)
        created += 1

    await db.flush()
    print(f"  StageGates: {created} created, {skipped} already existed")


# ─────────────────────────────────────────────────────────────────────────────
# L11 — Compliance Requirements
# ─────────────────────────────────────────────────────────────────────────────

async def seed_compliance(db: AsyncSession) -> None:
    """
    For each template in ALL_TEMPLATES:
      check by (framework + clause), insert ComplianceRequirement if missing
    """
    created = 0
    skipped = 0

    for template in ALL_TEMPLATES:
        result = await db.execute(
            select(ComplianceRequirement).where(
                ComplianceRequirement.framework == template["framework"],
                ComplianceRequirement.clause == template["clause"],
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            skipped += 1
            continue

        req = ComplianceRequirement(
            framework=template["framework"],
            clause=template["clause"],
            title=template["title"],
            description=template.get("description", ""),
            applies_to=template.get("applies_to", ""),
        )
        db.add(req)
        created += 1

    await db.flush()
    print(f"  ComplianceRequirements: {created} created, {skipped} already existed")


# ─────────────────────────────────────────────────────────────────────────────
# L12 — Quality Metrics
# ─────────────────────────────────────────────────────────────────────────────

async def seed_quality_metrics(db: AsyncSession) -> None:
    """
    For each item in QUALITY_METRICS: check by name, insert QualityMetric if missing
    """
    created = 0
    skipped = 0

    for item in QUALITY_METRICS:
        result = await db.execute(
            select(QualityMetric).where(QualityMetric.name == item["name"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            skipped += 1
            continue

        metric = QualityMetric(
            name=item["name"],
            description=item.get("description", ""),
            target_value=item["target_value"],
            unit=item.get("unit", ""),
        )
        db.add(metric)
        created += 1

    await db.flush()
    print(f"  QualityMetrics: {created} created, {skipped} already existed")


# ─────────────────────────────────────────────────────────────────────────────
# L13 — Impact Assessments & Surveys
# ─────────────────────────────────────────────────────────────────────────────

async def seed_impact(db: AsyncSession) -> None:
    """
    For each item in IMPACT_ASSESSMENTS: check by title, insert if missing.
    For each item in SURVEYS: check by title, insert if missing.
    """
    ia_created = 0
    ia_skipped = 0

    for item in IMPACT_ASSESSMENTS:
        result = await db.execute(
            select(ImpactAssessment).where(ImpactAssessment.title == item["title"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            ia_skipped += 1
            continue

        assessment = ImpactAssessment(
            title=item["title"],
            category=item.get("category", ""),
            description=item.get("description", ""),
            risk_level=item.get("risk_level", "low"),
            mitigation=item.get("mitigation", ""),
        )
        db.add(assessment)
        ia_created += 1

    await db.flush()
    print(f"  ImpactAssessments: {ia_created} created, {ia_skipped} already existed")

    sv_created = 0
    sv_skipped = 0

    for item in SURVEYS:
        result = await db.execute(
            select(Survey).where(Survey.title == item["title"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            sv_skipped += 1
            continue

        survey = Survey(
            title=item["title"],
            questions=item.get("questions", []),
        )
        db.add(survey)
        sv_created += 1

    await db.flush()
    print(f"  Surveys: {sv_created} created, {sv_skipped} already existed")


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

async def run_content_seed() -> None:
    """Execute the full Engineering Harnessing content seed."""
    print("\n" + "=" * 70)
    print("  TakiOS — Engineering Harnessing Content Seed")
    print("  Layers: L02, L04, L05, L09, L11, L12, L13")
    print("=" * 70)

    async with async_session() as db:
        try:
            # ── Admin user ────────────────────────────────────────────────
            print("\n👤 Ensuring admin user...")
            admin_id = await ensure_admin_user(db)

            # ── Fetch existing curriculum data ────────────────────────────
            print("\n📋 Loading existing curriculum data...")
            level_ids = await get_level_ids(db)
            module_ids = await get_module_ids(db)
            unit_ids = await get_unit_ids(db, module_ids)

            # ── L02: Tech Units & Chains ──────────────────────────────────
            print("\n⚙️  Seeding L02 — Tech Units...")
            tech_unit_ids = await seed_tech_units(db, level_ids)

            print("\n🔗 Seeding L02 — Tech Unit Chains...")
            await seed_tech_chains(db, level_ids, tech_unit_ids)

            # ── L09: Stage Gates ──────────────────────────────────────────
            print("\n🚦 Seeding L09 — Stage Gate Criteria...")
            await seed_stage_gates(db)

            # ── L11: Compliance ───────────────────────────────────────────
            print("\n⚖️  Seeding L11 — Compliance Requirements...")
            await seed_compliance(db)

            # ── L12: Quality Metrics ──────────────────────────────────────
            print("\n📊 Seeding L12 — Quality Metrics...")
            await seed_quality_metrics(db)

            # ── L13: Impact & Surveys ─────────────────────────────────────
            print("\n🌍 Seeding L13 — Impact Assessments & Surveys...")
            await seed_impact(db)

            # ── L04: Content & ContentVersions ────────────────────────────
            print("\n📄 Seeding L04 — Content & Content Versions...")
            content_ids = await seed_content(db, unit_ids, admin_id)

            # ── L04: Mnemonics ────────────────────────────────────────────
            print("\n🧠 Seeding L04 — Mnemonics (Eselsbrücken)...")
            await seed_mnemonics(db, content_ids, admin_id)

            # ── L05: Questions ────────────────────────────────────────────
            print("\n❓ Seeding L05 — Question Bank...")
            question_map = await seed_questions(db, unit_ids)

            # ── L05: Exams ────────────────────────────────────────────────
            print("\n📝 Seeding L05 — Exams...")
            await seed_exams(db, admin_id, module_ids, question_map)

            # ── Commit ────────────────────────────────────────────────────
            await db.commit()

            # ── Summary ───────────────────────────────────────────────────
            total_questions = sum(len(ids) for ids in question_map.values())
            total_content = len(content_ids)

            print("\n" + "=" * 70)
            print("  SEED COMPLETE")
            print("=" * 70)
            print(f"  TechUnits:            {len(tech_unit_ids)}")
            print(f"  TechChains:           {len(TECH_CHAINS)}")
            print(f"  StageGates:           {len(STAGE_GATE_DATA)}")
            print(f"  ComplianceReqs:       {len(ALL_TEMPLATES)}")
            print(f"  QualityMetrics:       {len(QUALITY_METRICS)}")
            print(f"  ImpactAssessments:    {len(IMPACT_ASSESSMENTS)}")
            print(f"  Surveys:              {len(SURVEYS)}")
            print(f"  ContentEntries:       {total_content}")
            print(f"  Mnemonics:            {len(MNEMONIC_DATA)}")
            print(f"  Questions:            {total_questions}")
            print(f"  Exams:                {len(question_map)}")
            print("=" * 70 + "\n")

        except Exception as e:
            await db.rollback()
            print(f"\n  SEED FAILED: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(run_content_seed())
