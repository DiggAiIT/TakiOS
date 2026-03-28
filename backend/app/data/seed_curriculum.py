"""
Seed script: Populate the TakiOS database with the complete
HAW Hamburg Medizintechnik PO 2025 curriculum.

Usage:
    cd backend
    python -m app.data.seed_curriculum
"""

from __future__ import annotations

import asyncio
import sys
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, engine, Base
from app.shared.base_model import AuditBase  # noqa: F401 — triggers model registration

# Import ALL layer models so SQLAlchemy knows about them
from app.layers.L01_level_selection.models import KnowledgeLevel, UserLevelProgress  # noqa: F401
from app.layers.L03_subjects_modules.models import (  # noqa: F401
    Module,
    ModulePrerequisite,
    ModuleUnit,
    Subject,
)
from app.layers.L06_project_creation.models import (  # noqa: F401
    Project,
    ProjectArtifact,
    ProjectMilestone,
)

from app.data.curriculum_data import (
    COMPLEXITY_LEVELS,
    MODULES,
    SUBJECTS,
    ModuleDef,
    SubjectDef,
)


async def seed_subjects(db: AsyncSession) -> dict[str, uuid.UUID]:
    """Seed all Subject records. Returns {subject_code: id}."""
    subject_ids: dict[str, uuid.UUID] = {}

    for s in SUBJECTS:
        # Check if already exists
        result = await db.execute(
            select(Subject).where(Subject.name_de == s.name_de)
        )
        existing = result.scalar_one_or_none()
        if existing:
            subject_ids[s.code] = existing.id
            print(f"  ✓ Subject exists: {s.name_de}")
            continue

        subject = Subject(
            name_de=s.name_de,
            name_en=s.name_en,
            description_de=s.description_de,
            description_en=s.description_en,
            department="Medizintechnik",
        )
        db.add(subject)
        await db.flush()
        subject_ids[s.code] = subject.id
        print(f"  + Subject created: {s.name_de}")

    return subject_ids


async def seed_modules(
    db: AsyncSession, subject_ids: dict[str, uuid.UUID]
) -> dict[str, uuid.UUID]:
    """Seed all Module records. Returns {module_code: id}."""
    module_ids: dict[str, uuid.UUID] = {}

    for m in MODULES:
        # Check if already exists
        result = await db.execute(
            select(Module).where(Module.code == m.code)
        )
        existing = result.scalar_one_or_none()
        if existing:
            module_ids[m.code] = existing.id
            print(f"  ✓ Module exists: {m.code} — {m.name_de}")
            continue

        module = Module(
            subject_id=subject_ids[m.subject_code],
            code=m.code,
            name_de=m.name_de,
            name_en=m.name_en,
            semester=m.semester,
            credits=m.credits,
            description_de=m.description_de,
            description_en=m.description_en,
        )
        db.add(module)
        await db.flush()
        module_ids[m.code] = module.id
        print(f"  + Module created: {m.code} — {m.name_de} (Sem {m.semester}, {m.credits} CP)")

    return module_ids


async def seed_module_units(
    db: AsyncSession, module_ids: dict[str, uuid.UUID]
) -> None:
    """Seed ModuleUnit records for every module."""
    for m in MODULES:
        mid = module_ids[m.code]
        # Check if units already seeded
        result = await db.execute(
            select(ModuleUnit).where(ModuleUnit.module_id == mid)
        )
        existing = list(result.scalars().all())
        if existing:
            print(f"  ✓ Units exist for {m.code} ({len(existing)} units)")
            continue

        for pos, title in enumerate(m.units, start=1):
            unit = ModuleUnit(
                module_id=mid,
                position=pos,
                title_de=title,
                title_en=title,  # Same for now; can be translated later
            )
            db.add(unit)
        await db.flush()
        print(f"  + {len(m.units)} units created for {m.code}")


async def seed_prerequisites(
    db: AsyncSession, module_ids: dict[str, uuid.UUID]
) -> None:
    """Seed ModulePrerequisite relationships."""
    for m in MODULES:
        if not m.prerequisites:
            continue

        mid = module_ids[m.code]
        for prereq_code in m.prerequisites:
            if prereq_code not in module_ids:
                print(f"  ⚠ Prerequisite {prereq_code} not found for {m.code}")
                continue

            prereq_id = module_ids[prereq_code]
            # Check if already exists
            result = await db.execute(
                select(ModulePrerequisite).where(
                    ModulePrerequisite.module_id == mid,
                    ModulePrerequisite.prerequisite_id == prereq_id,
                )
            )
            if result.scalar_one_or_none():
                continue

            prereq = ModulePrerequisite(
                module_id=mid,
                prerequisite_id=prereq_id,
            )
            db.add(prereq)

    await db.flush()
    print("  + Prerequisites seeded")


async def seed_knowledge_levels(
    db: AsyncSession, module_ids: dict[str, uuid.UUID]
) -> None:
    """Seed KnowledgeLevel entries from complexity levels."""
    for pos, cl in enumerate(COMPLEXITY_LEVELS, start=1):
        result = await db.execute(
            select(KnowledgeLevel).where(KnowledgeLevel.name_de == cl.name_de)
        )
        existing = result.scalar_one_or_none()
        if existing:
            print(f"  ✓ Level exists: {cl.level} — {cl.name_de}")
            continue

        level = KnowledgeLevel(
            name_de=f"Level {cl.level}: {cl.name_de}",
            name_en=f"Level {cl.level}: {cl.name_en}",
            description_de=cl.description_de,
            description_en=cl.description_en,
            pyramid_position=pos,
            unlock_criteria={
                "required_module_codes": cl.required_module_codes,
                "example_products": cl.example_products,
            },
        )
        db.add(level)
        print(f"  + Level created: {cl.level} — {cl.name_de}")

    await db.flush()


async def run_seed() -> None:
    """Execute the full curriculum seed."""
    print("\n" + "=" * 70)
    print("  TakiOS — HAW Hamburg Medizintechnik PO 2025 Curriculum Seed")
    print("=" * 70)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("\n✅ Database tables created/verified\n")

    async with async_session() as db:
        try:
            print("📚 Seeding Subjects (Fachgebiete)...")
            subject_ids = await seed_subjects(db)

            print(f"\n📖 Seeding Modules ({len(MODULES)} Module)...")
            module_ids = await seed_modules(db, subject_ids)

            print("\n📝 Seeding Module Units (Lerneinheiten)...")
            await seed_module_units(db, module_ids)

            print("\n🔗 Seeding Prerequisites (Voraussetzungen)...")
            await seed_prerequisites(db, module_ids)

            print("\n🏔️  Seeding Knowledge Levels (Komplexitätsstufen)...")
            await seed_knowledge_levels(db, module_ids)

            await db.commit()

            # Summary
            print("\n" + "=" * 70)
            print("  ✅ SEED COMPLETE")
            print("=" * 70)
            print(f"  Subjects:   {len(SUBJECTS)}")
            print(f"  Modules:    {len(MODULES)}")
            total_units = sum(len(m.units) for m in MODULES)
            print(f"  Units:      {total_units}")
            total_prereqs = sum(len(m.prerequisites) for m in MODULES)
            print(f"  Prereqs:    {total_prereqs}")
            print(f"  Levels:     {len(COMPLEXITY_LEVELS)}")
            print("=" * 70 + "\n")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Seed failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(run_seed())
