#!/usr/bin/env python3
"""Seed the database with HAW Hamburg Medizintechnik curriculum.

Run: python -m scripts.seed_medizintechnik
Or:  docker compose exec backend python -m scripts.seed_medizintechnik

This populates L01 (pyramid levels), L02 (tech units, chains),
L03 (subjects, modules, units), L04 (content, versions),
and L05 (questions, exams) with real Medizintechnik curriculum data.
"""

import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.layers.L01_level_selection.models import KnowledgeLevel
from app.layers.L02_tech_units.models import TechUnit, TechUnitChain, TechUnitChainLink
from app.layers.L03_subjects_modules.models import Module, ModuleUnit, Subject
from app.layers.L04_content_eselsbruecken.models import Content, ContentVersion
from app.layers.L05_knowledge_assessment.models import (
    BloomLevel,
    Difficulty,
    Exam,
    ExamQuestion,
    ExamType,
    QuestionBank,
    QuestionType,
)
from app.core.auth.models import User, UserRole

engine = create_async_engine(settings.database_url, echo=False)
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _id() -> uuid.UUID:
    return uuid.uuid4()


ADMIN_ID = _id()  # Seed admin user


# ---------------------------------------------------------------------------
# Subjects — core HAW Medizintechnik disciplines
# ---------------------------------------------------------------------------

SUBJECTS: list[dict] = [
    {
        "name_de": "Anatomie & Physiologie",
        "name_en": "Anatomy & Physiology",
        "description_de": "Aufbau und Funktion des menschlichen Körpers — Grundlage jeder Medizintechnik.",
        "description_en": "Structure and function of the human body — foundation of all biomedical engineering.",
    },
    {
        "name_de": "Physik",
        "name_en": "Physics",
        "description_de": "Mechanik, Optik, Akustik, Strahlung — physikalische Prinzipien medizintechnischer Geräte.",
        "description_en": "Mechanics, optics, acoustics, radiation — physics behind medical devices.",
    },
    {
        "name_de": "Elektrotechnik",
        "name_en": "Electrical Engineering",
        "description_de": "Schaltungstechnik, Signalverarbeitung und Sensorik für medizinische Anwendungen.",
        "description_en": "Circuit design, signal processing, and sensors for medical applications.",
    },
    {
        "name_de": "Informatik",
        "name_en": "Computer Science",
        "description_de": "Programmierung, Datenstrukturen und Software-Engineering in der Medizintechnik.",
        "description_en": "Programming, data structures, and software engineering in biomedical tech.",
    },
    {
        "name_de": "Medizinische Gerätetechnik",
        "name_en": "Medical Device Technology",
        "description_de": "Entwurf, Bau und Zulassung medizintechnischer Geräte nach MDR/IEC.",
        "description_en": "Design, manufacturing, and regulatory approval of medical devices (MDR/IEC).",
    },
    {
        "name_de": "Biomechanik",
        "name_en": "Biomechanics",
        "description_de": "Mechanische Eigenschaften biologischer Gewebe und Implantate.",
        "description_en": "Mechanical properties of biological tissues and implants.",
    },
    {
        "name_de": "Qualitätsmanagement & Regulatorik",
        "name_en": "Quality Management & Regulatory Affairs",
        "description_de": "ISO 13485, IEC 62304, MDR — Qualität und Zulassung in der Medizintechnik.",
        "description_en": "ISO 13485, IEC 62304, MDR — quality and regulatory compliance.",
    },
]

# ---------------------------------------------------------------------------
# Modules per Subject — roughly follows HAW Hamburg curriculum
# ---------------------------------------------------------------------------

# (subject_index, code, name_de, name_en, semester, credits, desc_de, desc_en)
MODULES: list[tuple] = [
    # Anatomie & Physiologie
    (0, "AP-101", "Anatomie I", "Anatomy I", 1, 5,
     "Allgemeine Anatomie: Zelle, Gewebe, Bewegungsapparat.",
     "General anatomy: cell, tissue, musculoskeletal system."),
    (0, "AP-102", "Physiologie I", "Physiology I", 1, 5,
     "Herz-Kreislauf, Atmung, Nervensystem.",
     "Cardiovascular, respiratory, nervous system."),
    (0, "AP-201", "Anatomie II", "Anatomy II", 2, 5,
     "Organsysteme: Verdauung, Niere, Endokrinologie.",
     "Organ systems: digestion, kidney, endocrinology."),

    # Physik
    (1, "PH-101", "Physik I", "Physics I", 1, 5,
     "Mechanik, Thermodynamik, Schwingungen.",
     "Mechanics, thermodynamics, oscillations."),
    (1, "PH-201", "Physik II", "Physics II", 2, 5,
     "Optik, Akustik, Strahlung.",
     "Optics, acoustics, radiation."),
    (1, "PH-301", "Medizinische Physik", "Medical Physics", 3, 5,
     "Röntgen, Ultraschall, MRT — physikalische Grundlagen bildgebender Verfahren.",
     "X-ray, ultrasound, MRI — physics of medical imaging."),

    # Elektrotechnik
    (2, "ET-101", "Elektrotechnik I", "Electrical Eng. I", 1, 5,
     "Gleichstrom, Wechselstrom, Bauelemente.",
     "DC, AC circuits, electronic components."),
    (2, "ET-201", "Elektrotechnik II", "Electrical Eng. II", 2, 5,
     "Messtechnik, Operationsverstärker, Filter.",
     "Measurement technology, op-amps, filters."),
    (2, "ET-301", "Biosignalverarbeitung", "Biosignal Processing", 3, 5,
     "EKG, EEG, EMG — Erfassung und digitale Verarbeitung.",
     "ECG, EEG, EMG — acquisition and digital processing."),

    # Informatik
    (3, "IN-101", "Programmierung I", "Programming I", 1, 5,
     "Grundlagen der Programmierung mit Python.",
     "Programming fundamentals with Python."),
    (3, "IN-201", "Programmierung II", "Programming II", 2, 5,
     "Objektorientierung, Datenstrukturen, Algorithmen.",
     "OOP, data structures, algorithms."),
    (3, "IN-301", "Software-Engineering", "Software Engineering", 3, 5,
     "IEC 62304, agile Methoden, Versionierung, Testing.",
     "IEC 62304, agile methods, version control, testing."),

    # Medizinische Gerätetechnik
    (4, "MG-301", "Gerätetechnik I", "Device Technology I", 3, 5,
     "Patientenmonitoring, Infusionstechnik, Beatmung.",
     "Patient monitoring, infusion, ventilation."),
    (4, "MG-401", "Gerätetechnik II", "Device Technology II", 4, 5,
     "Bildgebende Systeme: CT, MRT, Ultraschall.",
     "Imaging systems: CT, MRI, ultrasound."),
    (4, "MG-501", "Labormedizintechnik", "Lab Medicine Technology", 5, 5,
     "In-vitro-Diagnostik, Blutgasanalyse, Hämatologie.",
     "In-vitro diagnostics, blood gas analysis, hematology."),

    # Biomechanik
    (5, "BM-301", "Biomechanik I", "Biomechanics I", 3, 5,
     "Knochen, Gelenke, Muskeln — mechanische Modelle.",
     "Bones, joints, muscles — mechanical models."),
    (5, "BM-401", "Implantattechnik", "Implant Technology", 4, 5,
     "Werkstoffe, Biokompatibilität, Hüft-/Knieendoprothesen.",
     "Materials, biocompatibility, hip/knee prostheses."),

    # QM & Regulatorik
    (6, "QR-401", "Qualitätsmanagement", "Quality Management", 4, 5,
     "ISO 13485, CAPA, Risikomanagement nach ISO 14971.",
     "ISO 13485, CAPA, risk management per ISO 14971."),
    (6, "QR-501", "Regulatorische Zulassung", "Regulatory Affairs", 5, 5,
     "MDR, CE-Kennzeichnung, klinische Bewertung.",
     "MDR, CE marking, clinical evaluation."),
]

# ---------------------------------------------------------------------------
# Learning Units per Module — 3-4 per module
# ---------------------------------------------------------------------------

# (module_code, position, title_de, title_en)
UNITS: list[tuple] = [
    # AP-101 Anatomie I
    ("AP-101", 1, "Die Zelle — Aufbau und Funktion", "The Cell — Structure and Function"),
    ("AP-101", 2, "Gewebetypen", "Tissue Types"),
    ("AP-101", 3, "Knochen und Skelett", "Bones and Skeleton"),
    ("AP-101", 4, "Muskulatur", "Muscular System"),

    # AP-102 Physiologie I
    ("AP-102", 1, "Herz-Kreislauf-System", "Cardiovascular System"),
    ("AP-102", 2, "Atmungssystem", "Respiratory System"),
    ("AP-102", 3, "Nervensystem — Grundlagen", "Nervous System — Basics"),

    # AP-201 Anatomie II
    ("AP-201", 1, "Verdauungssystem", "Digestive System"),
    ("AP-201", 2, "Niere und Harnwege", "Kidney and Urinary Tract"),
    ("AP-201", 3, "Endokrines System", "Endocrine System"),

    # PH-101 Physik I
    ("PH-101", 1, "Mechanik — Kräfte und Bewegung", "Mechanics — Forces and Motion"),
    ("PH-101", 2, "Thermodynamik", "Thermodynamics"),
    ("PH-101", 3, "Schwingungen und Wellen", "Oscillations and Waves"),

    # PH-201 Physik II
    ("PH-201", 1, "Geometrische Optik", "Geometric Optics"),
    ("PH-201", 2, "Akustik und Ultraschall", "Acoustics and Ultrasound"),
    ("PH-201", 3, "Ionisierende Strahlung", "Ionizing Radiation"),

    # PH-301 Medizinische Physik
    ("PH-301", 1, "Röntgenstrahlung und Radiologie", "X-Rays and Radiology"),
    ("PH-301", 2, "Ultraschallbildgebung", "Ultrasound Imaging"),
    ("PH-301", 3, "Magnetresonanztomographie (MRT)", "Magnetic Resonance Imaging (MRI)"),

    # ET-101 Elektrotechnik I
    ("ET-101", 1, "Gleichstromkreise", "DC Circuits"),
    ("ET-101", 2, "Wechselstromkreise", "AC Circuits"),
    ("ET-101", 3, "Passive Bauelemente", "Passive Components"),

    # ET-201 Elektrotechnik II
    ("ET-201", 1, "Operationsverstärker", "Operational Amplifiers"),
    ("ET-201", 2, "Filter und Frequenzgang", "Filters and Frequency Response"),
    ("ET-201", 3, "Digitale Messtechnik", "Digital Measurement"),

    # ET-301 Biosignalverarbeitung
    ("ET-301", 1, "EKG — Elektrokardiogramm", "ECG — Electrocardiogram"),
    ("ET-301", 2, "EEG — Elektroenzephalogramm", "EEG — Electroencephalogram"),
    ("ET-301", 3, "Digitale Signalverarbeitung", "Digital Signal Processing"),

    # IN-101 Programmierung I
    ("IN-101", 1, "Variablen, Datentypen und Kontrollfluss", "Variables, Data Types, Control Flow"),
    ("IN-101", 2, "Funktionen und Module", "Functions and Modules"),
    ("IN-101", 3, "Listen, Dictionaries und Dateien", "Lists, Dictionaries, and Files"),

    # IN-201 Programmierung II
    ("IN-201", 1, "Klassen und Objekte", "Classes and Objects"),
    ("IN-201", 2, "Datenstrukturen", "Data Structures"),
    ("IN-201", 3, "Algorithmen und Komplexität", "Algorithms and Complexity"),

    # IN-301 Software-Engineering
    ("IN-301", 1, "Software-Lebenszyklus nach IEC 62304", "Software Lifecycle per IEC 62304"),
    ("IN-301", 2, "Agile Methoden und Scrum", "Agile Methods and Scrum"),
    ("IN-301", 3, "Versionierung mit Git", "Version Control with Git"),
    ("IN-301", 4, "Testing-Strategien", "Testing Strategies"),

    # MG-301 Gerätetechnik I
    ("MG-301", 1, "Patientenmonitoring — Vitalparameter", "Patient Monitoring — Vital Signs"),
    ("MG-301", 2, "Infusionstechnik", "Infusion Technology"),
    ("MG-301", 3, "Beatmungstechnik", "Ventilation Technology"),

    # MG-401 Gerätetechnik II
    ("MG-401", 1, "Computertomographie (CT)", "Computed Tomography (CT)"),
    ("MG-401", 2, "MRT-Systeme", "MRI Systems"),
    ("MG-401", 3, "Ultraschallgeräte", "Ultrasound Devices"),

    # MG-501 Labormedizintechnik
    ("MG-501", 1, "In-vitro-Diagnostik", "In-Vitro Diagnostics"),
    ("MG-501", 2, "Blutgasanalyse", "Blood Gas Analysis"),
    ("MG-501", 3, "Hämatologie-Analysatoren", "Hematology Analyzers"),

    # BM-301 Biomechanik I
    ("BM-301", 1, "Mechanik des Knochens", "Mechanics of Bone"),
    ("BM-301", 2, "Gelenkmechanik", "Joint Mechanics"),
    ("BM-301", 3, "Muskelmechanik", "Muscle Mechanics"),

    # BM-401 Implantattechnik
    ("BM-401", 1, "Biokompatible Werkstoffe", "Biocompatible Materials"),
    ("BM-401", 2, "Hüftendoprothesen", "Hip Prostheses"),
    ("BM-401", 3, "Knieendoprothesen", "Knee Prostheses"),

    # QR-401 Qualitätsmanagement
    ("QR-401", 1, "ISO 13485 — QMS für Medizinprodukte", "ISO 13485 — QMS for Medical Devices"),
    ("QR-401", 2, "Risikomanagement nach ISO 14971", "Risk Management per ISO 14971"),
    ("QR-401", 3, "CAPA — Korrektur- und Vorbeugemaßnahmen", "CAPA — Corrective and Preventive Actions"),

    # QR-501 Regulatorische Zulassung
    ("QR-501", 1, "Medical Device Regulation (MDR)", "Medical Device Regulation (MDR)"),
    ("QR-501", 2, "CE-Kennzeichnung und Konformität", "CE Marking and Conformity"),
    ("QR-501", 3, "Klinische Bewertung", "Clinical Evaluation"),
]

# ---------------------------------------------------------------------------
# Content (Markdown) for selected units — enough to demonstrate the system
# ---------------------------------------------------------------------------

CONTENT: dict[str, str] = {
    # Die Zelle
    ("AP-101", 1): """# Die Zelle — Aufbau und Funktion

## Grundstruktur

Die Zelle ist die kleinste funktionelle Einheit des Lebens. Jede menschliche Zelle enthält:

- **Zellmembran**: Lipid-Doppelschicht, selektiv permeabel
- **Zytoplasma**: Gelartiges Medium mit Organellen
- **Zellkern (Nukleus)**: Enthält die DNA, steuert Genexpression

## Organellen

| Organell | Funktion |
|---|---|
| Mitochondrien | ATP-Produktion (Zellatmung) |
| Endoplasmatisches Retikulum (ER) | Proteinsynthese (raues ER), Lipidsynthese (glattes ER) |
| Golgi-Apparat | Modifikation und Sortierung von Proteinen |
| Lysosomen | Intrazelluläre Verdauung |
| Ribosomen | Translation von mRNA zu Proteinen |

## Medizintechnische Relevanz

- **Zellkultur**: Grundlage für Biokompatibilitätstests (ISO 10993)
- **Membranpotential**: Basis für EKG, EEG, EMG — Biosignale entstehen durch Ionenflüsse
- **Apoptose vs. Nekrose**: Wichtig für die Bewertung von Implantatverträglichkeit
""",

    # Herz-Kreislauf
    ("AP-102", 1): """# Herz-Kreislauf-System

## Das Herz

Das Herz ist ein muskuläres Hohlorgan mit vier Kammern:

- **Rechter Vorhof** → **Rechter Ventrikel** → Lungenkreislauf
- **Linker Vorhof** → **Linker Ventrikel** → Körperkreislauf

### Erregungsleitungssystem

1. **Sinusknoten** (SA-Knoten) — primärer Schrittmacher (~70 bpm)
2. **AV-Knoten** — Verzögerung für koordinierte Kontraktion
3. **His-Bündel** → **Tawara-Schenkel** → **Purkinje-Fasern**

## EKG-Grundlagen

Das Elektrokardiogramm misst die elektrische Aktivität des Herzens:

- **P-Welle**: Vorhof-Depolarisation
- **QRS-Komplex**: Ventrikel-Depolarisation
- **T-Welle**: Ventrikel-Repolarisation

## Medizintechnische Geräte

- **EKG-Gerät**: 12-Kanal-Ableitung, Einthoven & Goldberger
- **Herzschrittmacher**: Implantierbare Pulsgeneratoren
- **Defibrillatoren**: AED und ICD
- **Herz-Lungen-Maschine**: Extrakorporale Zirkulation
""",

    # EKG
    ("ET-301", 1): """# EKG — Elektrokardiogramm

## Prinzip

Das EKG erfasst die Summe aller elektrischen Potentiale des Herzens über Elektroden auf der Körperoberfläche.

## Ableitsysteme

### Einthoven-Ableitungen (bipolar)
- **I**: Rechter Arm → Linker Arm
- **II**: Rechter Arm → Linkes Bein
- **III**: Linker Arm → Linkes Bein

### Goldberger-Ableitungen (unipolar, augmentiert)
- **aVR**, **aVL**, **aVF**

### Wilson-Brustwandableitungen
- **V1** bis **V6**: Präkordiale Positionen

## Signalverarbeitung

1. **Verstärkung**: Differenzverstärker (CMRR > 100 dB)
2. **Filterung**: Hochpass 0,05 Hz, Tiefpass 150 Hz, Netzfilter 50 Hz
3. **Digitalisierung**: ADC mit ≥ 12 Bit, Abtastrate ≥ 500 Hz

## Störungen

- **Netzbrummen** (50 Hz): Notch-Filter
- **Muskelartefakte**: Patient ruhig lagern
- **Basislinien-Drift**: Hochpassfilter oder digitale Korrektur

## Klinische Bedeutung

- Rhythmusstörungen (Arrhythmien)
- Myokardinfarkt (ST-Strecken-Hebung)
- Hypertrophie (erhöhte Amplituden)
""",

    # Röntgen
    ("PH-301", 1): """# Röntgenstrahlung und Radiologie

## Erzeugung von Röntgenstrahlung

Röntgenstrahlen entstehen in einer **Röntgenröhre**:

1. Elektronen werden aus der Kathode (Glühkathode) emittiert
2. Beschleunigung durch Hochspannung (30–150 kV)
3. Abbremsung an der Anode → **Bremsstrahlung**
4. Ionisation innerer Schalen → **Charakteristische Strahlung**

## Wechselwirkungen mit Materie

| Effekt | Energie | Bedeutung |
|---|---|---|
| Photoeffekt | Niedrig | Kontrast in der Diagnostik |
| Compton-Streuung | Mittel | Streustrahlung → Bildqualitätsminderung |
| Paarbildung | > 1,022 MeV | Nur in der Strahlentherapie relevant |

## Bildgebung

- **Konventionelles Röntgen**: Projektionsbild, 2D
- **Computertomographie**: Schnittbilder durch Rotation, 3D-Rekonstruktion
- **Dosisgrößen**: Kerma, Einfalldosis, effektive Dosis (mSv)

## Strahlenschutz

- **ALARA-Prinzip**: As Low As Reasonably Achievable
- **Abstand, Abschirmung, Aufenthaltsdauer**
- Bleiäquivalentwerte für Schutzkleidung
""",

    # ISO 13485
    ("QR-401", 1): """# ISO 13485 — Qualitätsmanagementsystem für Medizinprodukte

## Überblick

ISO 13485 definiert Anforderungen an ein QMS speziell für die Medizintechnik-Branche. Sie ergänzt und erweitert ISO 9001 um regulatorische Aspekte.

## Kernelemente

### 4. Qualitätsmanagementsystem
- Dokumentierte Prozesse und Verfahren
- Lenkung von Dokumenten und Aufzeichnungen
- QM-Handbuch

### 5. Verantwortung der Leitung
- Verpflichtung der Leitung
- Qualitätspolitik und -ziele
- Management-Review

### 7. Produktrealisierung
- **Design und Entwicklung**: Input → Review → Verifizierung → Validierung → Transfer
- **Beschaffung**: Lieferantenbewertung
- **Produktion**: Prozessvalidierung, Rückverfolgbarkeit

### 8. Messung, Analyse und Verbesserung
- Überwachung und Messung
- Internes Audit
- CAPA (Korrektur- und Vorbeugemaßnahmen)

## Zusammenhang mit MDR

Die MDR (EU 2017/745) fordert ein QMS gemäß ISO 13485 als Voraussetzung für die CE-Kennzeichnung.
""",

    # Gleichstromkreise
    ("ET-101", 1): """# Gleichstromkreise

## Grundgrößen

| Größe | Symbol | Einheit | Beschreibung |
|---|---|---|---|
| Spannung | U | Volt (V) | Potentialdifferenz |
| Strom | I | Ampere (A) | Ladungsträgerbewegung |
| Widerstand | R | Ohm (Ω) | Fließhemmung |

## Ohmsches Gesetz

$$U = R \\cdot I$$

## Kirchhoffsche Regeln

### Knotenregel (1. Kirchhoffsches Gesetz)
Die Summe aller Ströme an einem Knoten ist Null:
$$\\sum I_k = 0$$

### Maschenregel (2. Kirchhoffsches Gesetz)
Die Summe aller Spannungen in einer Masche ist Null:
$$\\sum U_k = 0$$

## Reihen- und Parallelschaltung

**Reihenschaltung**: $R_{ges} = R_1 + R_2 + \\ldots$

**Parallelschaltung**: $\\frac{1}{R_{ges}} = \\frac{1}{R_1} + \\frac{1}{R_2} + \\ldots$

## Medizintechnische Relevanz

- Patientenableitströme (IEC 60601-1): < 10 µA normal, < 50 µA bei Einzelfehler
- Isolationswiderstand medizinischer Geräte
- Erdung und Schutzklassen (Typ B, BF, CF)
""",

    # Programmierung I — Variablen
    ("IN-101", 1): """# Variablen, Datentypen und Kontrollfluss

## Variablen in Python

```python
# Zuweisung
name = "TakiOS"
version = 1.0
active = True
```

## Datentypen

| Typ | Beispiel | Beschreibung |
|---|---|---|
| `int` | `42` | Ganzzahl |
| `float` | `3.14` | Gleitkommazahl |
| `str` | `"Hallo"` | Zeichenkette |
| `bool` | `True` | Wahrheitswert |
| `list` | `[1, 2, 3]` | Geordnete Sammlung |
| `dict` | `{"key": "val"}` | Schlüssel-Wert-Paare |

## Kontrollfluss

### Bedingte Ausführung
```python
blutdruck = 140
if blutdruck > 130:
    print("Hypertonie — Warnung!")
elif blutdruck < 90:
    print("Hypotonie — Warnung!")
else:
    print("Normaler Blutdruck")
```

### Schleifen
```python
# Vitalparameter-Monitoring
messwerte = [98.6, 99.1, 97.8, 100.2]
for temp in messwerte:
    if temp > 100.0:
        print(f"Fieber erkannt: {temp}°F")
```

## Medizintechnische Anwendung

Python wird in der Medizintechnik eingesetzt für:
- Datenanalyse (Biosignale, klinische Studien)
- Machine Learning (Bildklassifikation in CT/MRT)
- Gerätesteuerung (Raspberry Pi, Sensorik)
""",

    # IEC 62304
    ("IN-301", 1): """# Software-Lebenszyklus nach IEC 62304

## Überblick

IEC 62304 definiert den Software-Lebenszyklus für medizinische Software:

- **Klasse A**: Kein Schaden möglich
- **Klasse B**: Nicht-schwere Verletzung möglich
- **Klasse C**: Tod oder schwere Verletzung möglich

## Prozesse

### 1. Software-Entwicklungsplanung
- Entwicklungsmethodik festlegen
- Werkzeuge und Infrastruktur definieren
- Risikomanagement-Integration planen

### 2. Software-Anforderungsanalyse
- Funktionale und nicht-funktionale Anforderungen
- Rückverfolgbarkeit zu Systemanforderungen

### 3. Software-Architektur
- Zerlegung in Software-Einheiten
- Schnittstellen definieren
- SOUP (Software of Unknown Provenance) identifizieren

### 4. Detailliertes Design
- Nur für Klasse B und C erforderlich
- Algorithmen und Datenstrukturen beschreiben

### 5. Implementierung und Verifikation
- Coding Standards einhalten
- Code Review und Unit Tests

### 6. Integration und Integrationstests
- Software-Einheiten zusammenführen
- Schnittstellentests

### 7. Systemtest
- Validierung gegen Anforderungen

## TakiOS-Relevanz

TakiOS wendet IEC 62304 Klasse B Praktiken freiwillig an — als Qualitätsnachweis und Thesis-Argument.
""",
}

# ---------------------------------------------------------------------------
# Questions for selected modules
# ---------------------------------------------------------------------------

# (module_code, unit_position, question_de, question_en, type, options, correct, difficulty, bloom)
QUESTIONS: list[tuple] = [
    # Anatomie I — Die Zelle
    ("AP-101", 1,
     "Welche Organelle ist hauptsächlich für die ATP-Produktion verantwortlich?",
     "Which organelle is primarily responsible for ATP production?",
     QuestionType.MULTIPLE_CHOICE,
     {"options": ["Ribosom", "Mitochondrium", "Golgi-Apparat", "Lysosom"]},
     {"answer": "Mitochondrium"},
     Difficulty.EASY, BloomLevel.REMEMBER),

    ("AP-101", 1,
     "Was ist die Funktion des rauen endoplasmatischen Retikulums?",
     "What is the function of the rough endoplasmic reticulum?",
     QuestionType.MULTIPLE_CHOICE,
     {"options": ["Lipidsynthese", "Proteinsynthese", "ATP-Produktion", "DNA-Replikation"]},
     {"answer": "Proteinsynthese"},
     Difficulty.EASY, BloomLevel.REMEMBER),

    ("AP-101", 1,
     "Warum ist das Membranpotential der Zelle für die Medizintechnik relevant?",
     "Why is the cell membrane potential relevant for biomedical engineering?",
     QuestionType.FREE_TEXT,
     None,
     {"answer": "Das Membranpotential ist die Grundlage für Biosignale wie EKG, EEG und EMG."},
     Difficulty.MEDIUM, BloomLevel.UNDERSTAND),

    # Physiologie I — Herz-Kreislauf
    ("AP-102", 1,
     "Welcher Knoten ist der primäre Schrittmacher des Herzens?",
     "Which node is the primary pacemaker of the heart?",
     QuestionType.MULTIPLE_CHOICE,
     {"options": ["AV-Knoten", "Sinusknoten", "His-Bündel", "Purkinje-Fasern"]},
     {"answer": "Sinusknoten"},
     Difficulty.EASY, BloomLevel.REMEMBER),

    ("AP-102", 1,
     "Ordne die EKG-Wellen den kardialen Ereignissen zu: P-Welle, QRS-Komplex, T-Welle.",
     "Match the ECG waves to cardiac events: P-wave, QRS complex, T-wave.",
     QuestionType.MATCHING,
     {"pairs": [
         {"left": "P-Welle", "right": "Vorhof-Depolarisation"},
         {"left": "QRS-Komplex", "right": "Ventrikel-Depolarisation"},
         {"left": "T-Welle", "right": "Ventrikel-Repolarisation"},
     ]},
     {"answer": [
         {"left": "P-Welle", "right": "Vorhof-Depolarisation"},
         {"left": "QRS-Komplex", "right": "Ventrikel-Depolarisation"},
         {"left": "T-Welle", "right": "Ventrikel-Repolarisation"},
     ]},
     Difficulty.MEDIUM, BloomLevel.UNDERSTAND),

    # EKG — Biosignalverarbeitung
    ("ET-301", 1,
     "Welche minimale Abtastrate wird für ein diagnostisches EKG empfohlen?",
     "What minimum sampling rate is recommended for a diagnostic ECG?",
     QuestionType.MULTIPLE_CHOICE,
     {"options": ["100 Hz", "250 Hz", "500 Hz", "1000 Hz"]},
     {"answer": "500 Hz"},
     Difficulty.MEDIUM, BloomLevel.REMEMBER),

    ("ET-301", 1,
     "Was ist der Zweck eines Notch-Filters im EKG-Gerät?",
     "What is the purpose of a notch filter in an ECG device?",
     QuestionType.MULTIPLE_CHOICE,
     {"options": [
         "Verstärkung des QRS-Komplexes",
         "Entfernung der 50-Hz-Netzstörung",
         "Basislinien-Korrektur",
         "Erhöhung der Abtastrate",
     ]},
     {"answer": "Entfernung der 50-Hz-Netzstörung"},
     Difficulty.EASY, BloomLevel.UNDERSTAND),

    # Elektrotechnik I — Gleichstrom
    ("ET-101", 1,
     "Wie lautet das Ohmsche Gesetz?",
     "What is Ohm's Law?",
     QuestionType.MULTIPLE_CHOICE,
     {"options": ["U = R · I", "P = U · I", "I = U · R", "R = I / U"]},
     {"answer": "U = R · I"},
     Difficulty.EASY, BloomLevel.REMEMBER),

    ("ET-101", 1,
     "Wie groß ist der Gesamtwiderstand von zwei 100Ω-Widerständen in Parallelschaltung?",
     "What is the total resistance of two 100Ω resistors in parallel?",
     QuestionType.MULTIPLE_CHOICE,
     {"options": ["200 Ω", "100 Ω", "50 Ω", "25 Ω"]},
     {"answer": "50 Ω"},
     Difficulty.MEDIUM, BloomLevel.APPLY),

    # Röntgen
    ("PH-301", 1,
     "Welches Prinzip liegt dem Strahlenschutz zugrunde?",
     "Which principle underlies radiation protection?",
     QuestionType.MULTIPLE_CHOICE,
     {"options": ["FIFO-Prinzip", "ALARA-Prinzip", "Pareto-Prinzip", "LIFO-Prinzip"]},
     {"answer": "ALARA-Prinzip"},
     Difficulty.EASY, BloomLevel.REMEMBER),

    # QM — ISO 13485
    ("QR-401", 1,
     "Welcher Standard definiert das QMS für Medizinprodukte?",
     "Which standard defines the QMS for medical devices?",
     QuestionType.MULTIPLE_CHOICE,
     {"options": ["ISO 9001", "ISO 13485", "ISO 14971", "IEC 62304"]},
     {"answer": "ISO 13485"},
     Difficulty.EASY, BloomLevel.REMEMBER),

    ("QR-401", 1,
     "Was bedeutet CAPA?",
     "What does CAPA stand for?",
     QuestionType.MULTIPLE_CHOICE,
     {"options": [
         "Clinical Assessment and Patient Analysis",
         "Corrective and Preventive Actions",
         "Compliance Audit for Product Approval",
         "Central Authority for Product Assessment",
     ]},
     {"answer": "Corrective and Preventive Actions"},
     Difficulty.EASY, BloomLevel.REMEMBER),

    # IEC 62304
    ("IN-301", 1,
     "Welche Software-Sicherheitsklasse nach IEC 62304 erfordert das detaillierte Design?",
     "Which IEC 62304 software safety class requires detailed design?",
     QuestionType.MULTIPLE_CHOICE,
     {"options": ["Nur Klasse A", "Klasse A und B", "Klasse B und C", "Alle Klassen"]},
     {"answer": "Klasse B und C"},
     Difficulty.MEDIUM, BloomLevel.UNDERSTAND),

    # Programmierung I
    ("IN-101", 1,
     "Welcher Datentyp speichert Wahrheitswerte in Python?",
     "Which data type stores truth values in Python?",
     QuestionType.MULTIPLE_CHOICE,
     {"options": ["int", "str", "bool", "float"]},
     {"answer": "bool"},
     Difficulty.EASY, BloomLevel.REMEMBER),
]

# ---------------------------------------------------------------------------
# L01: Knowledge Pyramid Levels (bottom=1, top=7)
# ---------------------------------------------------------------------------

# (position, name_de, name_en, desc_de, desc_en, unlock_criteria)
PYRAMID_LEVELS: list[tuple] = [
    (1, "Binär (0/1)", "Binary (0/1)",
     "Die fundamentale Sprache aller digitalen Systeme. Alles beginnt mit 0 und 1.",
     "The fundamental language of all digital systems. Everything starts with 0 and 1.",
     None),  # Base level — always unlocked
    (2, "Physik & Logik", "Physics & Logic",
     "Physikalische Gesetze und logische Grundlagen — von Ohm bis Boole.",
     "Physical laws and logical foundations — from Ohm to Boole.",
     {"required_module_codes": ["PH-101"]}),
    (3, "Elektronik", "Electronics",
     "Schaltungen, Verstärker, Filter — die Bausteine medizintechnischer Geräte.",
     "Circuits, amplifiers, filters — the building blocks of medical devices.",
     {"required_module_codes": ["ET-101", "ET-201"]}),
    (4, "Hardware", "Hardware",
     "Sensoren, Aktoren, Mikroprozessoren — von der Schaltung zum System.",
     "Sensors, actuators, microprocessors — from circuit to system.",
     {"required_module_codes": ["ET-301", "MG-301"]}),
    (5, "Netzwerk", "Network",
     "Kommunikation zwischen Geräten — DICOM, HL7/FHIR und Klinik-IT.",
     "Device communication — DICOM, HL7/FHIR and hospital IT.",
     {"required_module_codes": ["IN-201", "MG-401"]}),
    (6, "Software", "Software",
     "Programmierung, Architektur, Lebenszyklus — Software als Medizinprodukt.",
     "Programming, architecture, lifecycle — software as a medical device.",
     {"required_module_codes": ["IN-101", "IN-301"]}),
    (7, "KI / Robotik", "AI / Robotics",
     "Maschinelles Lernen, Bildanalyse, Chirurgie-Roboter — die Spitze der Pyramide.",
     "Machine learning, image analysis, surgical robots — the pyramid's peak.",
     {"required_module_codes": ["IN-201", "PH-301", "MG-401"]}),
]

# ---------------------------------------------------------------------------
# L02: Tech Units — (level_position, name_de, name_en, desc_de, desc_en, io_spec, limitations)
# ---------------------------------------------------------------------------

TECH_UNITS: list[tuple] = [
    # Level 1: Binary
    (1, "Binäres Zahlensystem", "Binary Number System",
     "Darstellung von Zahlen im Binärsystem (Basis 2).",
     "Representing numbers in binary (base 2).",
     {"input": "Dezimalzahl", "output": "Binärfolge"},
     "Begrenzt auf diskrete Werte"),
    (1, "Logikgatter", "Logic Gates",
     "AND, OR, NOT, XOR — die Grundbausteine digitaler Schaltungen.",
     "AND, OR, NOT, XOR — the building blocks of digital circuits.",
     {"input": "Binäre Signale", "output": "Binäres Signal"},
     "Nur boolesche Operationen"),
    (1, "Boolesche Algebra", "Boolean Algebra",
     "Mathematische Grundlage für logische Operationen.",
     "Mathematical foundation for logical operations.",
     {"input": "Logischer Ausdruck", "output": "Vereinfachter Ausdruck"},
     "Begrenzt auf zwei Zustände"),

    # Level 2: Physics/Logic
    (2, "Ohmsches Gesetz", "Ohm's Law",
     "U = R · I — Zusammenhang von Spannung, Widerstand und Strom.",
     "U = R · I — relationship between voltage, resistance, and current.",
     {"input": "Zwei der drei Größen (U, R, I)", "output": "Dritte Größe"},
     "Nur für ohmsche Widerstände gültig"),
    (2, "Kirchhoffsche Regeln", "Kirchhoff's Laws",
     "Knoten- und Maschenregel für Netzwerkanalyse.",
     "Node and mesh rules for network analysis.",
     {"input": "Schaltungstopologie", "output": "Strom-/Spannungsverteilung"},
     "Ideal; vernachlässigt parasitäre Effekte"),
    (2, "Elektromagnetische Wellen", "Electromagnetic Waves",
     "Ausbreitung, Reflexion, Absorption — Grundlage für Bildgebung.",
     "Propagation, reflection, absorption — foundation for imaging.",
     {"input": "Wellenlänge/Frequenz", "output": "Wechselwirkung mit Gewebe"},
     "Frequenzabhängige Absorption"),

    # Level 3: Electronics
    (3, "Operationsverstärker", "Operational Amplifier",
     "Universeller Verstärkerbaustein in der Biosignalverarbeitung.",
     "Universal amplifier building block in biosignal processing.",
     {"input": "Differenzspannung (µV–mV)", "output": "Verstärkte Spannung (V)"},
     "Endliche Bandbreite und Slew Rate"),
    (3, "ADC / DAC", "ADC / DAC",
     "Analog-Digital- und Digital-Analog-Wandlung.",
     "Analog-to-digital and digital-to-analog conversion.",
     {"input": "Analoges / Digitales Signal", "output": "Digitales / Analoges Signal"},
     "Quantisierungsrauschen, Aliasing bei zu niedriger Abtastrate"),
    (3, "Filter", "Filters",
     "Tiefpass, Hochpass, Bandpass, Notch — Frequenzselektion.",
     "Low-pass, high-pass, band-pass, notch — frequency selection.",
     {"input": "Rohes Signal", "output": "Gefiltertes Signal"},
     "Phasenverschiebung, Grenzfrequenz-Kompromiss"),

    # Level 4: Hardware
    (4, "Medizinische Elektroden", "Medical Electrodes",
     "Ag/AgCl-Elektroden für EKG, EEG, EMG.",
     "Ag/AgCl electrodes for ECG, EEG, EMG.",
     {"input": "Bioelektrisches Potential", "output": "Elektrisches Signal"},
     "Kontaktimpedanz, Bewegungsartefakte"),
    (4, "Sensoren", "Sensors",
     "Temperatur, Druck, SpO₂, Durchfluss — medizinische Sensorik.",
     "Temperature, pressure, SpO₂, flow — medical sensors.",
     {"input": "Physikalische Größe", "output": "Elektrisches Signal"},
     "Drift, Kalibrierungsbedarf"),
    (4, "Mikroprozessoren", "Microprocessors",
     "Embedded Systems für medizintechnische Geräte.",
     "Embedded systems for medical devices.",
     {"input": "Digitale Signale, Code", "output": "Steuerungssignale, Daten"},
     "Begrenzte Rechenleistung, Echtzeitanforderungen"),

    # Level 5: Network
    (5, "DICOM", "DICOM",
     "Digital Imaging and Communications in Medicine — Standard für medizinische Bilder.",
     "Digital Imaging and Communications in Medicine — medical imaging standard.",
     {"input": "Medizinisches Bild + Metadaten", "output": "DICOM-Datei"},
     "Große Dateien, komplexer Standard"),
    (5, "HL7 / FHIR", "HL7 / FHIR",
     "Health Level 7 / FHIR — Interoperabilitätsstandards für Gesundheitsdaten.",
     "Health Level 7 / FHIR — interoperability standards for health data.",
     {"input": "Klinische Daten", "output": "Standardisierte Nachrichten/Ressourcen"},
     "Implementierungsvarianten, Mapping-Aufwand"),
    (5, "Serielle Protokolle", "Serial Protocols",
     "UART, SPI, I²C — Kommunikation auf Geräteebene.",
     "UART, SPI, I²C — device-level communication.",
     {"input": "Digitale Daten", "output": "Serielle Bitfolge"},
     "Begrenzte Reichweite und Datenrate"),

    # Level 6: Software
    (6, "Python", "Python",
     "Programmiersprache für Datenanalyse, ML und Gerätesteuerung.",
     "Programming language for data analysis, ML, and device control.",
     {"input": "Quellcode", "output": "Ausführbare Logik"},
     "Langsamer als C/C++ für Echtzeit"),
    (6, "Versionskontrolle (Git)", "Version Control (Git)",
     "Änderungsverfolgung und Kollaboration nach IEC 62304.",
     "Change tracking and collaboration per IEC 62304.",
     {"input": "Codeänderungen", "output": "Versioniertes Repository"},
     "Lernkurve, Merge-Konflikte"),
    (6, "Software-Testing", "Software Testing",
     "Unit, Integration, System — Verifikation nach IEC 62304.",
     "Unit, integration, system — verification per IEC 62304.",
     {"input": "Software + Testfälle", "output": "Testergebnisse, Coverage"},
     "Nicht alle Fehler durch Tests findbar"),

    # Level 7: AI/Robotics
    (7, "Machine Learning", "Machine Learning",
     "Klassifikation, Regression, Clustering für medizinische Daten.",
     "Classification, regression, clustering for medical data.",
     {"input": "Trainingsdaten", "output": "Trainiertes Modell"},
     "Datenqualität, Erklärbarkeit (XAI)"),
    (7, "Neuronale Netze", "Neural Networks",
     "CNNs für Bildanalyse, RNNs für Zeitreihen (EKG, EEG).",
     "CNNs for image analysis, RNNs for time series (ECG, EEG).",
     {"input": "Features / Rohdaten", "output": "Vorhersage / Klassifikation"},
     "Black Box, hoher Rechenaufwand"),
    (7, "Medizinische Bildanalyse", "Medical Image Analysis",
     "Automatische Erkennung von Pathologien in CT, MRT, Röntgen.",
     "Automated detection of pathologies in CT, MRI, X-ray.",
     {"input": "Medizinisches Bild", "output": "Segmentierung / Diagnose"},
     "Regulatorische Hürden (MDR Klasse IIa+)"),
]

# ---------------------------------------------------------------------------
# L02: Tech Unit Chains — (level_position, name, desc, [unit_name_en, ...])
# ---------------------------------------------------------------------------

TECH_CHAINS: list[tuple] = [
    (3, "Biosignal-Aufbereitung",
     "Verstärkung, Filterung und Digitalisierung von Biosignalen.",
     ["Operational Amplifier", "Filters", "ADC / DAC"]),
    (5, "Klinischer Datenaustausch",
     "Vom Gerät über serielle Schnittstelle zu standardisierten Gesundheitsdaten.",
     ["Serial Protocols", "HL7 / FHIR", "DICOM"]),
    (7, "KI-Diagnostik-Pipeline",
     "Automatische Analyse medizinischer Bilder mittels Deep Learning.",
     ["Machine Learning", "Neural Networks", "Medical Image Analysis"]),
]


# ---------------------------------------------------------------------------
# Main seed function
# ---------------------------------------------------------------------------

async def seed():
    async with Session() as db:
        # 1. Seed admin user
        print("  Creating seed admin user...")
        admin = User(
            id=ADMIN_ID,
            email="admin@takios.de",
            full_name="TakiOS Admin",
            hashed_password="$2b$12$LJ3m4ys3Lk0Tn5Y7v1r6XOjHkNQB1G5K8T2x3J9Q4Y5Z6A7B8C9D",  # placeholder
            role=UserRole.ADMIN,
        )
        db.add(admin)
        await db.flush()

        # 2. Seed subjects
        print("  Seeding subjects...")
        subject_objs: list[Subject] = []
        for s in SUBJECTS:
            subject = Subject(**s)
            db.add(subject)
            subject_objs.append(subject)
        await db.flush()

        # 3. Seed modules
        print("  Seeding modules...")
        module_map: dict[str, Module] = {}  # code -> Module
        for subj_idx, code, name_de, name_en, semester, credits, desc_de, desc_en in MODULES:
            module = Module(
                subject_id=subject_objs[subj_idx].id,
                code=code,
                name_de=name_de,
                name_en=name_en,
                semester=semester,
                credits=credits,
                description_de=desc_de,
                description_en=desc_en,
            )
            db.add(module)
            module_map[code] = module
        await db.flush()

        # 4. Seed module units
        print("  Seeding module units...")
        unit_map: dict[tuple[str, int], ModuleUnit] = {}  # (code, pos) -> ModuleUnit
        for code, position, title_de, title_en in UNITS:
            module = module_map[code]
            unit = ModuleUnit(
                module_id=module.id,
                position=position,
                title_de=title_de,
                title_en=title_en,
            )
            db.add(unit)
            unit_map[(code, position)] = unit
        await db.flush()

        # 5. Seed content & versions
        print("  Seeding content and versions...")
        content_map: dict[tuple[str, int], Content] = {}
        for (code, pos), markdown in CONTENT.items():
            unit = unit_map[(code, pos)]
            content = Content(module_unit_id=unit.id)
            db.add(content)
            await db.flush()

            version = ContentVersion(
                content_id=content.id,
                body_markdown=markdown.strip(),
                version_number=1,
                created_by=ADMIN_ID,
                change_reason="Initial content",
            )
            db.add(version)
            await db.flush()

            content.current_version_id = version.id
            content_map[(code, pos)] = content
        await db.flush()

        # 6. Seed questions
        print("  Seeding question bank...")
        question_map: dict[tuple[str, int, int], QuestionBank] = {}
        q_counter: dict[tuple[str, int], int] = {}
        for code, unit_pos, q_de, q_en, q_type, options, correct, diff, bloom in QUESTIONS:
            unit = unit_map[(code, unit_pos)]
            key = (code, unit_pos)
            q_counter[key] = q_counter.get(key, 0) + 1

            question = QuestionBank(
                module_unit_id=unit.id,
                question_type=q_type,
                question_de=q_de,
                question_en=q_en,
                answer_options=options,
                correct_answer=correct,
                difficulty=diff,
                bloom_level=bloom,
            )
            db.add(question)
            question_map[(code, unit_pos, q_counter[key])] = question
        await db.flush()

        # 7. Seed exams — one per module that has questions
        print("  Seeding exams...")
        modules_with_questions = set()
        for code, unit_pos, *_ in QUESTIONS:
            modules_with_questions.add(code)

        for code in sorted(modules_with_questions):
            module = module_map[code]
            exam = Exam(
                module_id=module.id,
                title=f"Klausur: {module.name_de}",
                exam_type=ExamType.DIGITAL,
                time_limit_minutes=30,
                created_by=ADMIN_ID,
            )
            db.add(exam)
            await db.flush()

            # Add all questions for this module
            position = 0
            for (q_code, q_pos, q_idx), question in question_map.items():
                if q_code == code:
                    position += 1
                    eq = ExamQuestion(
                        exam_id=exam.id,
                        question_id=question.id,
                        position=position,
                        points=1.0,
                    )
                    db.add(eq)
            await db.flush()

        # 8. Seed pyramid levels (L01)
        print("  Seeding knowledge pyramid levels...")
        level_map: dict[int, KnowledgeLevel] = {}  # position -> KnowledgeLevel
        for pos, name_de, name_en, desc_de, desc_en, criteria in PYRAMID_LEVELS:
            level = KnowledgeLevel(
                name_de=name_de,
                name_en=name_en,
                description_de=desc_de,
                description_en=desc_en,
                pyramid_position=pos,
                unlock_criteria=criteria,
            )
            db.add(level)
            level_map[pos] = level
        await db.flush()

        # Set parent relationships (each level's parent is the one below)
        for pos in range(2, 8):
            level_map[pos].parent_id = level_map[pos - 1].id
        await db.flush()

        # 9. Seed tech units (L02)
        print("  Seeding tech units...")
        tech_unit_map: dict[str, TechUnit] = {}  # name_en -> TechUnit
        for lvl_pos, name_de, name_en, desc_de, desc_en, io_spec, limitations in TECH_UNITS:
            tu = TechUnit(
                level_id=level_map[lvl_pos].id,
                name_de=name_de,
                name_en=name_en,
                description_de=desc_de,
                description_en=desc_en,
                io_spec=io_spec,
                limitations=limitations,
            )
            db.add(tu)
            tech_unit_map[name_en] = tu
        await db.flush()

        # 10. Seed tech unit chains (L02)
        print("  Seeding tech unit chains...")
        for lvl_pos, name, description, unit_names in TECH_CHAINS:
            chain = TechUnitChain(
                name=name,
                level_id=level_map[lvl_pos].id,
                description=description,
            )
            db.add(chain)
            await db.flush()

            for i, unit_name in enumerate(unit_names, start=1):
                tu = tech_unit_map[unit_name]
                link = TechUnitChainLink(
                    chain_id=chain.id,
                    tech_unit_id=tu.id,
                    position=i,
                )
                db.add(link)
            await db.flush()

        await db.commit()
        print("\n  Seed complete!")
        print(f"    {len(SUBJECTS)} subjects")
        print(f"    {len(MODULES)} modules")
        print(f"    {len(UNITS)} learning units")
        print(f"    {len(CONTENT)} content pages with Markdown")
        print(f"    {len(QUESTIONS)} questions")
        print(f"    {len(modules_with_questions)} exams")
        print(f"    {len(PYRAMID_LEVELS)} pyramid levels")
        print(f"    {len(TECH_UNITS)} tech units")
        print(f"    {len(TECH_CHAINS)} tech unit chains")


if __name__ == "__main__":
    print("\nSeeding HAW Hamburg Medizintechnik curriculum into TakiOS...\n")
    asyncio.run(seed())
