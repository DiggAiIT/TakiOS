"""API endpoint for the Project Analyzer — analyzes student project ideas."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.project_analyzer import project_analyzer


router = APIRouter()


class ProjectIdeaRequest(BaseModel):
    """Request body for analyzing a project idea."""

    idea: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Student's medical device project idea in free text",
        examples=["EKG-Wearable für Sportler mit Echtzeit-Herzrhythmus-Analyse"],
    )
    use_ai: bool = Field(
        default=True,
        description="Use AI for analysis (False = keyword-based fallback)",
    )


class LearningPhaseResponse(BaseModel):
    phase_number: int
    title_de: str
    title_en: str
    semester_equivalent: int
    module_codes: list[str]
    module_names: list[str]
    project_relevance: str


class ProjectAnalysisResponse(BaseModel):
    complexity_level: str
    complexity_name_de: str
    complexity_name_en: str
    reasoning: str
    required_module_codes: list[str]
    required_module_names: list[str]
    total_credits: int
    learning_path: list[LearningPhaseResponse]
    suggested_milestones: list[dict[str, str]]
    project_context: dict[str, str]


@router.post("/analyze", response_model=ProjectAnalysisResponse)
async def analyze_project_idea(request: ProjectIdeaRequest):
    """
    Analyze a student's medical device project idea.

    Returns:
    - Complexity level (A-E)
    - Required modules from the HAW Medizintechnik curriculum
    - Personalized learning path
    - Suggested project milestones
    """
    try:
        if request.use_ai:
            analysis = await project_analyzer.analyze_project_idea(request.idea)
        else:
            analysis = project_analyzer.analyze_project_idea_offline(request.idea)
    except Exception as e:
        # Fallback to offline if AI fails
        analysis = project_analyzer.analyze_project_idea_offline(request.idea)

    return ProjectAnalysisResponse(
        complexity_level=analysis.complexity_level,
        complexity_name_de=analysis.complexity_name_de,
        complexity_name_en=analysis.complexity_name_en,
        reasoning=analysis.reasoning,
        required_module_codes=[m.code for m in analysis.required_modules],
        required_module_names=[m.name_de for m in analysis.required_modules],
        total_credits=sum(m.credits for m in analysis.required_modules),
        learning_path=[
            LearningPhaseResponse(
                phase_number=p.phase_number,
                title_de=p.title_de,
                title_en=p.title_en,
                semester_equivalent=p.semester_equivalent,
                module_codes=[m.code for m in p.modules],
                module_names=[m.name_de for m in p.modules],
                project_relevance=p.project_relevance,
            )
            for p in analysis.learning_path
        ],
        suggested_milestones=analysis.suggested_milestones,
        project_context=analysis.project_context,
    )


class CurriculumOverviewResponse(BaseModel):
    total_subjects: int
    total_modules: int
    total_credits: int
    semesters: int
    modules_by_semester: dict[str, list[dict[str, str | int]]]


@router.get("/curriculum", response_model=CurriculumOverviewResponse)
async def get_curriculum_overview():
    """Get an overview of the complete HAW Medizintechnik PO 2025 curriculum."""
    from app.data.curriculum_data import MODULES, SUBJECTS, get_modules_by_semester

    modules_by_sem = get_modules_by_semester()
    formatted: dict[str, list[dict[str, str | int]]] = {}
    for sem, mods in sorted(modules_by_sem.items()):
        formatted[str(sem)] = [
            {
                "code": m.code,
                "name_de": m.name_de,
                "name_en": m.name_en,
                "credits": m.credits,
                "subject": m.subject_code,
            }
            for m in mods
        ]

    return CurriculumOverviewResponse(
        total_subjects=len(SUBJECTS),
        total_modules=len(MODULES),
        total_credits=sum(m.credits for m in MODULES),
        semesters=7,
        modules_by_semester=formatted,
    )


class ComplexityLevelResponse(BaseModel):
    level: str
    name_de: str
    name_en: str
    description_de: str
    description_en: str
    example_products: list[str]
    required_module_count: int


@router.get("/complexity-levels", response_model=list[ComplexityLevelResponse])
async def list_complexity_levels():
    """List all project complexity levels (A-E) with descriptions."""
    from app.data.curriculum_data import COMPLEXITY_LEVELS

    return [
        ComplexityLevelResponse(
            level=cl.level,
            name_de=cl.name_de,
            name_en=cl.name_en,
            description_de=cl.description_de,
            description_en=cl.description_en,
            example_products=cl.example_products,
            required_module_count=len(cl.required_module_codes),
        )
        for cl in COMPLEXITY_LEVELS
    ]
