"""
Project Analyzer Service — AI-powered analysis of medical device project ideas.

This service takes a student's project idea (e.g. "EKG-Wearable für Sportler")
and uses AI to:
1. Determine the complexity level (A-E)
2. Map the project to relevant HAW Hamburg Medizintechnik modules
3. Generate a personalized learning path
4. Create initial project milestones
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import anthropic

from app.config import settings
from app.data.curriculum_data import (
    COMPLEXITY_LEVELS,
    MODULES,
    ComplexityLevelDef,
    ModuleDef,
    get_module_lookup,
    get_prerequisite_graph,
)


@dataclass
class ProjectAnalysis:
    """Result of analyzing a project idea."""

    complexity_level: str  # A-E
    complexity_name_de: str
    complexity_name_en: str
    reasoning: str
    required_modules: list[ModuleDef]
    learning_path: list[LearningPhase]
    suggested_milestones: list[dict[str, str]]
    project_context: dict[str, str]  # context per module for personalization


@dataclass
class LearningPhase:
    """A phase in the personalized learning path."""

    phase_number: int
    title_de: str
    title_en: str
    semester_equivalent: int
    modules: list[ModuleDef]
    project_relevance: str  # Why these modules matter for the project


ANALYSIS_SYSTEM_PROMPT = """Du bist ein KI-Bildungsberater für den Studiengang Medizintechnik (B.Sc.) an der HAW Hamburg.

Deine Aufgabe:
1. Analysiere die Projektidee des Studenten
2. Bestimme das Komplexitäts-Level (A bis E)
3. Ordne die relevanten Module zu
4. Erstelle einen personalisierten Lernpfad
5. Schlage Meilensteine vor

Die Komplexitäts-Level sind:
- Level A: Einfaches Messgerät (Thermometer, Pulsoximeter)
- Level B: Signalverarbeitung (EKG-Wearable, EMG-Biofeedback)
- Level C: Software-Medizinprodukt / SaMD (Diagnose-App, Telemedizin)
- Level D: Implantierbares / Therapeutisches Gerät (Prothesen, Neurostimulator)
- Level E: Komplexes Gesamtsystem (MRT-Zubehör, Chirurgie-Roboter)

Antworte IMMER in diesem exakten JSON-Format:
{
    "complexity_level": "A|B|C|D|E",
    "reasoning": "Begründung für die Level-Wahl (2-3 Sätze)",
    "additional_modules": ["MT-XXX", ...],  // Module die über das Standard-Level hinaus nötig sind
    "project_context": {
        "MT-XXX": "Warum dieses Modul für das Projekt relevant ist (1 Satz)"
    },
    "suggested_milestones": [
        {"title": "Meilenstein-Titel", "description": "Kurze Beschreibung"}
    ],
    "learning_phases": [
        {
            "phase_number": 1,
            "title_de": "Phase-Titel",
            "title_en": "Phase Title",
            "semester_equivalent": 1,
            "module_codes": ["MT-M1", "MT-P1", ...],
            "project_relevance": "Warum diese Module jetzt wichtig sind"
        }
    ]
}"""


class ProjectAnalyzer:
    """Analyzes project ideas and generates personalized learning paths."""

    def __init__(self) -> None:
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key or "")
        self.module_lookup = get_module_lookup()

    async def analyze_project_idea(self, project_idea: str) -> ProjectAnalysis:
        """Analyze a project idea and return a full ProjectAnalysis."""

        # Build module catalog for the AI
        module_catalog = self._build_module_catalog()

        user_prompt = f"""Projektidee des Studenten:
\"{project_idea}\"

Verfügbare Module im Studiengang:
{module_catalog}

Analysiere diese Projektidee und erstelle einen personalisierten Lernpfad.
Antworte ausschließlich im JSON-Format wie in der Systembeschreibung angegeben."""

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=ANALYSIS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        raw_text = response.content[0].text
        analysis_data = json.loads(raw_text)

        return self._build_analysis(analysis_data)

    def analyze_project_idea_offline(self, project_idea: str) -> ProjectAnalysis:
        """
        Offline / fallback analysis without AI — uses keyword matching.
        Useful when AI is unavailable or for testing.
        """
        idea_lower = project_idea.lower()

        # Keyword-based level detection
        level = "A"  # default
        if any(kw in idea_lower for kw in ["implantat", "prothese", "stimulat", "pumpe", "cochlea"]):
            level = "D"
        elif any(kw in idea_lower for kw in ["mrt", "robot", "labor", "intensiv", "modular"]):
            level = "E"
        elif any(kw in idea_lower for kw in ["app", "software", "diagnose", "tele", "ki", "ai", "bild"]):
            level = "C"
        elif any(kw in idea_lower for kw in ["ekg", "eeg", "emg", "monitor", "signal", "wearable"]):
            level = "B"

        # Find matching complexity level
        cl = next((c for c in COMPLEXITY_LEVELS if c.level == level), COMPLEXITY_LEVELS[0])

        # Build required modules list
        required_modules = [
            self.module_lookup[code]
            for code in cl.required_module_codes
            if code in self.module_lookup
        ]

        # Build learning phases grouped by semester
        phases: list[LearningPhase] = []
        modules_by_sem: dict[int, list[ModuleDef]] = {}
        for m in required_modules:
            modules_by_sem.setdefault(m.semester, []).append(m)

        for i, (sem, mods) in enumerate(sorted(modules_by_sem.items()), start=1):
            phases.append(LearningPhase(
                phase_number=i,
                title_de=f"Phase {i}: Semester {sem}",
                title_en=f"Phase {i}: Semester {sem}",
                semester_equivalent=sem,
                modules=mods,
                project_relevance=f"Grundlagen für das Projekt (Semester {sem})",
            ))

        # Generate generic milestones
        milestones = [
            {"title": "Projektidee dokumentieren", "description": "Anforderungsanalyse und Pflichtenheft erstellen"},
            {"title": "Technisches Konzept", "description": "Systemarchitektur und Komponentenauswahl"},
            {"title": "Prototyp (Software)", "description": "MVP als Software-Simulation"},
            {"title": "Hardware-Prototyp", "description": "Erster physischer Prototyp"},
            {"title": "Validierung & Tests", "description": "Verifizierung und Validierung nach Normen"},
            {"title": "Dokumentation & Zulassung", "description": "Technische Dokumentation und regulatorische Vorbereitung"},
        ]

        return ProjectAnalysis(
            complexity_level=cl.level,
            complexity_name_de=cl.name_de,
            complexity_name_en=cl.name_en,
            reasoning=f"Basierend auf Schlüsselworten wurde Level {cl.level} ({cl.name_de}) bestimmt.",
            required_modules=required_modules,
            learning_path=phases,
            suggested_milestones=milestones,
            project_context={m.code: f"Relevant für {project_idea}" for m in required_modules},
        )

    def _build_module_catalog(self) -> str:
        """Build a text catalog of all modules for the AI prompt."""
        lines = []
        for m in MODULES:
            prereqs = ", ".join(m.prerequisites) if m.prerequisites else "keine"
            lines.append(
                f"- {m.code}: {m.name_de} (Sem {m.semester}, {m.credits} CP, Voraussetzungen: {prereqs})"
            )
        return "\n".join(lines)

    def _build_analysis(self, data: dict) -> ProjectAnalysis:
        """Convert raw AI JSON response into a ProjectAnalysis."""
        level_code = data.get("complexity_level", "A")
        cl = next(
            (c for c in COMPLEXITY_LEVELS if c.level == level_code),
            COMPLEXITY_LEVELS[0],
        )

        # Merge standard level modules + any additional modules from AI
        all_codes = set(cl.required_module_codes)
        additional = data.get("additional_modules", [])
        all_codes.update(additional)

        required_modules = [
            self.module_lookup[code]
            for code in all_codes
            if code in self.module_lookup
        ]

        # Build learning phases from AI response
        phases: list[LearningPhase] = []
        for phase_data in data.get("learning_phases", []):
            phase_modules = [
                self.module_lookup[code]
                for code in phase_data.get("module_codes", [])
                if code in self.module_lookup
            ]
            phases.append(LearningPhase(
                phase_number=phase_data.get("phase_number", 1),
                title_de=phase_data.get("title_de", ""),
                title_en=phase_data.get("title_en", ""),
                semester_equivalent=phase_data.get("semester_equivalent", 1),
                modules=phase_modules,
                project_relevance=phase_data.get("project_relevance", ""),
            ))

        return ProjectAnalysis(
            complexity_level=cl.level,
            complexity_name_de=cl.name_de,
            complexity_name_en=cl.name_en,
            reasoning=data.get("reasoning", ""),
            required_modules=required_modules,
            learning_path=phases,
            suggested_milestones=data.get("suggested_milestones", []),
            project_context=data.get("project_context", {}),
        )


# Singleton
project_analyzer = ProjectAnalyzer()
