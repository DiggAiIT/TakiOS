"""
HAW Hamburg — Medizintechnik / Biomedical Engineering B.Sc.
Prüfungs- und Studienordnung 2025 (PO 2025, gültig ab WS 2025/2026)

Vollständiger Studienverlaufsplan mit allen Modulen, Fachgebieten,
CP-Werten, Semesterzuordnungen und Prerequisite-Beziehungen.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ──────────────────────────────────────────────────────────────────────
# Fachgebiete (Subjects)
# ──────────────────────────────────────────────────────────────────────

@dataclass
class SubjectDef:
    code: str
    name_de: str
    name_en: str
    description_de: str
    description_en: str


SUBJECTS: list[SubjectDef] = [
    SubjectDef(
        code="MATH",
        name_de="Mathematik",
        name_en="Mathematics",
        description_de="Mathematische Grundlagen und Methoden für die Medizintechnik",
        description_en="Mathematical foundations and methods for biomedical engineering",
    ),
    SubjectDef(
        code="PHYS",
        name_de="Physik",
        name_en="Physics",
        description_de="Physikalische Grundlagen inkl. Mechanik, Elektromagnetismus, Optik",
        description_en="Physical foundations including mechanics, electromagnetism, optics",
    ),
    SubjectDef(
        code="ET",
        name_de="Elektrotechnik & Elektronik",
        name_en="Electrical Engineering & Electronics",
        description_de="Elektrotechnische Grundlagen, Schaltungstechnik, Signalverarbeitung",
        description_en="Electrical engineering fundamentals, circuit design, signal processing",
    ),
    SubjectDef(
        code="INF",
        name_de="Informatik & Softwaretechnik",
        name_en="Computer Science & Software Engineering",
        description_de="Programmierung, Algorithmen, medizinische Softwaretechnik",
        description_en="Programming, algorithms, medical software engineering",
    ),
    SubjectDef(
        code="MED",
        name_de="Medizin & Humanbiologie",
        name_en="Medicine & Human Biology",
        description_de="Anatomie, Physiologie, Zellbiologie, medizinisches Basiswissen",
        description_en="Anatomy, physiology, cell biology, medical foundation knowledge",
    ),
    SubjectDef(
        code="NAWI",
        name_de="Naturwissenschaften",
        name_en="Natural Sciences",
        description_de="Chemie, Biologie und naturwissenschaftliche Grundlagen",
        description_en="Chemistry, biology, and natural science foundations",
    ),
    SubjectDef(
        code="ING",
        name_de="Ingenieurwissenschaften",
        name_en="Engineering Sciences",
        description_de="Mechanik, Strömungslehre, Thermodynamik, Biomechanik",
        description_en="Mechanics, fluid dynamics, thermodynamics, biomechanics",
    ),
    SubjectDef(
        code="MESS",
        name_de="Messtechnik & Sensorik",
        name_en="Measurement & Sensor Technology",
        description_de="Messtechnik, Sensortechnik, bildgebende Verfahren, Regelungstechnik",
        description_en="Measurement technology, sensors, imaging, control engineering",
    ),
    SubjectDef(
        code="REG",
        name_de="Regulatorik & Qualitätsmanagement",
        name_en="Regulatory Affairs & Quality Management",
        description_de="MDR, CE-Kennzeichnung, ISO 13485, ISO 14971, Risikoanalyse",
        description_en="MDR, CE marking, ISO 13485, ISO 14971, risk analysis",
    ),
    SubjectDef(
        code="MGMT",
        name_de="Management & Methodik",
        name_en="Management & Methodology",
        description_de="Projektmanagement, ingenieurwissenschaftliches Arbeiten, Wissenschaftsmethodik",
        description_en="Project management, engineering methodology, scientific methods",
    ),
    SubjectDef(
        code="PRAXIS",
        name_de="Praxis & Abschluss",
        name_en="Practical & Thesis",
        description_de="Praxissemester, Bachelorarbeit, Seminar, Wahlpflichtfächer",
        description_en="Internship, bachelor thesis, seminar, elective modules",
    ),
]


# ──────────────────────────────────────────────────────────────────────
# Module (Courses)
# ──────────────────────────────────────────────────────────────────────

@dataclass
class ModuleDef:
    code: str
    subject_code: str
    name_de: str
    name_en: str
    semester: int
    credits: int
    description_de: str
    description_en: str
    prerequisites: list[str] = field(default_factory=list)
    units: list[str] = field(default_factory=list)


MODULES: list[ModuleDef] = [
    # ── SEMESTER 1 ──────────────────────────────────────────────────
    ModuleDef(
        code="MT-M1",
        subject_code="MATH",
        name_de="Mathematik 1",
        name_en="Mathematics 1",
        semester=1,
        credits=5,
        description_de="Lineare Algebra, Vektorrechnung, Differentialrechnung, Funktionsanalyse",
        description_en="Linear algebra, vector calculus, differential calculus, function analysis",
        units=[
            "Lineare Gleichungssysteme & Matrizen",
            "Vektorrechnung im R²/R³",
            "Differentialrechnung einer Veränderlichen",
            "Kurvendiskussion & Extremwertprobleme",
            "Komplexe Zahlen",
        ],
    ),
    ModuleDef(
        code="MT-P1",
        subject_code="PHYS",
        name_de="Physik 1",
        name_en="Physics 1",
        semester=1,
        credits=5,
        description_de="Mechanik, Schwingungen, Wellen, Akustik",
        description_en="Mechanics, oscillations, waves, acoustics",
        units=[
            "Kinematik & Dynamik",
            "Arbeit, Energie, Leistung",
            "Drehbewegung & Drehmoment",
            "Schwingungen & Resonanz",
            "Wellen & Akustik",
        ],
    ),
    ModuleDef(
        code="MT-ET1",
        subject_code="ET",
        name_de="Elektrotechnik 1",
        name_en="Electrical Engineering 1",
        semester=1,
        credits=5,
        description_de="Gleichstromnetze, Kirchhoffsche Gesetze, Widerstände, Kondensatoren, Spulen",
        description_en="DC circuits, Kirchhoff's laws, resistors, capacitors, inductors",
        units=[
            "Grundgrößen (Strom, Spannung, Widerstand)",
            "Kirchhoffsche Gesetze",
            "Reihen- und Parallelschaltungen",
            "Kondensatoren & elektrisches Feld",
            "Spulen & magnetisches Feld",
        ],
    ),
    ModuleDef(
        code="MT-INF1",
        subject_code="INF",
        name_de="Informatik 1 + Praktikum",
        name_en="Computer Science 1 + Lab",
        semester=1,
        credits=5,
        description_de="Grundlagen der Programmierung (Python/C), Algorithmen, Datenstrukturen, Praktikum",
        description_en="Programming fundamentals (Python/C), algorithms, data structures, lab",
        units=[
            "Einführung in die Programmierung",
            "Variablen, Datentypen, Kontrollstrukturen",
            "Funktionen & Modularität",
            "Arrays, Listen, Dictionaries",
            "Dateien & Fehlerbehandlung",
            "Praktikum: Implementierungsprojekt",
        ],
    ),
    ModuleDef(
        code="MT-HB1",
        subject_code="MED",
        name_de="Humanbiologie 1 (Anatomie & Physiologie)",
        name_en="Human Biology 1 (Anatomy & Physiology)",
        semester=1,
        credits=5,
        description_de="Zellaufbau, Gewebearten, Bewegungsapparat, Herz-Kreislauf-System",
        description_en="Cell structure, tissue types, musculoskeletal system, cardiovascular system",
        units=[
            "Zellbiologie & Zellorganellen",
            "Grundgewebearten",
            "Knochen, Gelenke, Skelettmuskulatur",
            "Herz: Aufbau & Erregungsleitung",
            "Blutkreislauf & Gefäßsystem",
        ],
    ),
    ModuleDef(
        code="MT-CH",
        subject_code="NAWI",
        name_de="Chemie",
        name_en="Chemistry",
        semester=1,
        credits=5,
        description_de="Allgemeine und organische Chemie, Biochemie-Grundlagen",
        description_en="General and organic chemistry, biochemistry basics",
        units=[
            "Atombau & Periodensystem",
            "Chemische Bindungen",
            "Säuren, Basen, pH-Wert",
            "Organische Chemie (Kohlenwasserstoffe, funktionelle Gruppen)",
            "Biochemie: Proteine, Lipide, Kohlenhydrate",
        ],
    ),

    # ── SEMESTER 2 ──────────────────────────────────────────────────
    ModuleDef(
        code="MT-M2",
        subject_code="MATH",
        name_de="Mathematik 2",
        name_en="Mathematics 2",
        semester=2,
        credits=5,
        description_de="Integralrechnung, Differentialgleichungen, Reihenentwicklungen",
        description_en="Integral calculus, differential equations, series expansions",
        prerequisites=["MT-M1"],
        units=[
            "Integralrechnung (bestimmt/unbestimmt)",
            "Integrationsmethoden",
            "Gewöhnliche Differentialgleichungen 1. Ordnung",
            "DGL 2. Ordnung mit konst. Koeffizienten",
            "Taylor- und Fourier-Reihen",
        ],
    ),
    ModuleDef(
        code="MT-P2",
        subject_code="PHYS",
        name_de="Physik 2",
        name_en="Physics 2",
        semester=2,
        credits=5,
        description_de="Elektromagnetismus, Optik, Atom- und Kernphysik",
        description_en="Electromagnetism, optics, atomic and nuclear physics",
        prerequisites=["MT-P1"],
        units=[
            "Elektrisches Feld & Coulomb-Gesetz",
            "Magnetfeld & Induktion",
            "Elektromagnetische Wellen",
            "Geometrische & Wellenoptik",
            "Atom- und Kernphysik Grundlagen",
        ],
    ),
    ModuleDef(
        code="MT-ET2",
        subject_code="ET",
        name_de="Elektrotechnik 2",
        name_en="Electrical Engineering 2",
        semester=2,
        credits=5,
        description_de="Wechselstromtechnik, komplexe Rechnung, Filter, Transformatoren",
        description_en="AC circuits, complex notation, filters, transformers",
        prerequisites=["MT-ET1"],
        units=[
            "Wechselstromgrößen & Zeigerdiagramme",
            "Komplexe Wechselstromrechnung",
            "LC- und RC-Schaltungen",
            "Resonanz & Filterschaltungen",
            "Transformatoren & Übertrager",
        ],
    ),
    ModuleDef(
        code="MT-INF2",
        subject_code="INF",
        name_de="Informatik 2 + Praktikum",
        name_en="Computer Science 2 + Lab",
        semester=2,
        credits=5,
        description_de="Objektorientierte Programmierung, Software-Engineering, Datenbanken",
        description_en="Object-oriented programming, software engineering, databases",
        prerequisites=["MT-INF1"],
        units=[
            "Objektorientierung: Klassen, Vererbung",
            "Design Patterns Grundlagen",
            "Datenbanken & SQL",
            "Versionskontrolle (Git)",
            "Praktikum: OOP-Projekt",
        ],
    ),
    ModuleDef(
        code="MT-HB2",
        subject_code="MED",
        name_de="Humanbiologie 2 (Systeme & Organe)",
        name_en="Human Biology 2 (Systems & Organs)",
        semester=2,
        credits=5,
        description_de="Nervensystem, Respiratorisches System, Verdauung, Sinnesorgane",
        description_en="Nervous system, respiratory system, digestion, sensory organs",
        prerequisites=["MT-HB1"],
        units=[
            "Nervensystem: ZNS & PNS",
            "Sinnesorgane: Auge, Ohr",
            "Respiratorisches System",
            "Gastrointestinaltrakt",
            "Niere & Harnwege",
        ],
    ),
    ModuleDef(
        code="MT-STAT",
        subject_code="MATH",
        name_de="Statistik",
        name_en="Statistics",
        semester=2,
        credits=5,
        description_de="Deskriptive Statistik, Wahrscheinlichkeitstheorie, Hypothesentests",
        description_en="Descriptive statistics, probability theory, hypothesis testing",
        prerequisites=["MT-M1"],
        units=[
            "Deskriptive Statistik & Visualisierung",
            "Wahrscheinlichkeitsrechnung",
            "Verteilungen (Normal, Poisson, Binomial)",
            "Konfidenzintervalle & Hypothesentests",
            "Regression & Korrelation",
        ],
    ),

    # ── SEMESTER 3 ──────────────────────────────────────────────────
    ModuleDef(
        code="MT-M3",
        subject_code="MATH",
        name_de="Mathematik 3",
        name_en="Mathematics 3",
        semester=3,
        credits=5,
        description_de="Mehrdimensionale Analysis, Vektoranalysis, partielle DGL",
        description_en="Multivariable calculus, vector analysis, partial differential equations",
        prerequisites=["MT-M2"],
        units=[
            "Funktionen mehrerer Veränderlicher",
            "Partielle Ableitungen & Gradient",
            "Mehrfachintegrale",
            "Vektoranalysis (div, rot, grad)",
            "Partielle Differentialgleichungen (Einführung)",
        ],
    ),
    ModuleDef(
        code="MT-INF3",
        subject_code="INF",
        name_de="Informatik 3",
        name_en="Computer Science 3",
        semester=3,
        credits=3,
        description_de="Mikrokontroller-Programmierung, Embedded Systems, Echtzeitprogrammierung",
        description_en="Microcontroller programming, embedded systems, real-time programming",
        prerequisites=["MT-INF2"],
        units=[
            "Mikrokontroller-Architektur",
            "GPIO, ADC, Timer, Interrupts",
            "Embedded C Programmierung",
            "Echtzeitbetriebssysteme (Grundlagen)",
            "Kommunikationsprotokolle (SPI, I²C, UART)",
        ],
    ),
    ModuleDef(
        code="MT-EL1",
        subject_code="ET",
        name_de="Elektronik 1",
        name_en="Electronics 1",
        semester=3,
        credits=5,
        description_de="Halbleiter, Dioden, Transistoren, Operationsverstärker",
        description_en="Semiconductors, diodes, transistors, operational amplifiers",
        prerequisites=["MT-ET2"],
        units=[
            "Halbleiterphysik Grundlagen",
            "Dioden & Gleichrichterschaltungen",
            "Bipolar- & Feldeffekttransistoren",
            "Transistor-Grundschaltungen",
            "Operationsverstärker & Anwendungen",
        ],
    ),
    ModuleDef(
        code="MT-TM1",
        subject_code="ING",
        name_de="Technische Mechanik 1",
        name_en="Engineering Mechanics 1",
        semester=3,
        credits=5,
        description_de="Statik, Festigkeitslehre, Deformationen, Werkstoffkunde",
        description_en="Statics, strength of materials, deformations, material science",
        prerequisites=["MT-P1", "MT-M1"],
        units=[
            "Kraftsysteme & Gleichgewicht",
            "Schwerpunktsberechnung",
            "Spannungen & Dehnungen",
            "Biegung & Torsion",
            "Werkstoffkunde: Metalle, Polymere, Keramik",
        ],
    ),
    ModuleDef(
        code="MT-MS",
        subject_code="MESS",
        name_de="Messtechnik",
        name_en="Measurement Technology",
        semester=3,
        credits=5,
        description_de="Messprinzipien, Sensoren, Messunsicherheit, A/D-Wandlung",
        description_en="Measurement principles, sensors, uncertainty, A/D conversion",
        prerequisites=["MT-ET1", "MT-P1"],
        units=[
            "Messen, Messabweichung, Messunsicherheit",
            "Sensoren: resistiv, kapazitiv, induktiv",
            "Temperatur- & Druckmessung",
            "A/D- und D/A-Wandlung",
            "Messbrücken & Signalkonditionierung",
        ],
    ),
    ModuleDef(
        code="MT-ZMB",
        subject_code="NAWI",
        name_de="Zell- und Mikrobiologie",
        name_en="Cell & Microbiology",
        semester=3,
        credits=5,
        description_de="Zellbiologie, Mikroorganismen, Sterilisation, Biokompatibilität",
        description_en="Cell biology, microorganisms, sterilization, biocompatibility",
        prerequisites=["MT-HB1", "MT-CH"],
        units=[
            "Zellzyklus & Zellteilung",
            "Bakterien, Viren, Pilze",
            "Sterilisation & Desinfektion",
            "Immunsystem & Infektionslehre",
            "Biokompatibilität (Einführung ISO 10993)",
        ],
    ),
    ModuleDef(
        code="MT-IAW",
        subject_code="MGMT",
        name_de="Ingenieurwissenschaftliches Arbeiten",
        name_en="Engineering Methodology",
        semester=3,
        credits=3,
        description_de="Wissenschaftliches Schreiben, Recherche, Präsentation, Projektplanung",
        description_en="Scientific writing, research, presentation, project planning",
        units=[
            "Wissenschaftliches Schreiben",
            "Literaturrecherche & Quellenkritik",
            "Präsentationstechniken",
            "Zeitmanagement & Projektplanung",
        ],
    ),

    # ── SEMESTER 4 ──────────────────────────────────────────────────
    ModuleDef(
        code="MT-M4",
        subject_code="MATH",
        name_de="Mathematik 4",
        name_en="Mathematics 4",
        semester=4,
        credits=5,
        description_de="Laplace-/Z-Transformation, Numerische Methoden",
        description_en="Laplace/Z-transform, numerical methods",
        prerequisites=["MT-M3"],
        units=[
            "Laplace-Transformation",
            "Z-Transformation",
            "Numerische Integration & Differentiation",
            "Numerische Lösung von DGL",
            "Optimierungsmethoden",
        ],
    ),
    ModuleDef(
        code="MT-EL2",
        subject_code="ET",
        name_de="Elektronik 2",
        name_en="Electronics 2",
        semester=4,
        credits=5,
        description_de="Digitaltechnik, Schaltungsentwurf, Mixed-Signal-Schaltungen",
        description_en="Digital logic, circuit design, mixed-signal circuits",
        prerequisites=["MT-EL1"],
        units=[
            "Boolesche Algebra & Logikgatter",
            "Kombinatorische Schaltungen",
            "Sequentielle Schaltungen (Flip-Flops, Zähler)",
            "PCB-Design Grundlagen",
            "Mixed-Signal & EMV",
        ],
    ),
    ModuleDef(
        code="MT-SYS",
        subject_code="MESS",
        name_de="Systemtheorie & Signalverarbeitung",
        name_en="Systems Theory & Signal Processing",
        semester=4,
        credits=5,
        description_de="LTI-Systeme, Fourier-Transformation, digitale Filter, Abtasttheorem",
        description_en="LTI systems, Fourier transform, digital filters, sampling theorem",
        prerequisites=["MT-M3", "MT-ET2"],
        units=[
            "Zeitkontinuierliche Signale & Systeme",
            "Fourier-Reihe & Fourier-Transformation",
            "Abtasttheorem & Quantisierung",
            "Digitale Filter (FIR, IIR)",
            "Transferfunktionen & Bode-Diagramm",
        ],
    ),
    ModuleDef(
        code="MT-STR",
        subject_code="ING",
        name_de="Strömungslehre",
        name_en="Fluid Mechanics",
        semester=4,
        credits=5,
        description_de="Hydrostatik, Hydrodynamik, Navier-Stokes, Blutströmung",
        description_en="Hydrostatics, hydrodynamics, Navier-Stokes, blood flow",
        prerequisites=["MT-P1", "MT-M2"],
        units=[
            "Hydrostatik & Auftrieb",
            "Kontinuitätsgleichung & Bernoulli",
            "Viskosität & laminare/turbulente Strömung",
            "Navier-Stokes-Gleichungen (Einführung)",
            "Blutströmung & Hämodynamik",
        ],
    ),
    ModuleDef(
        code="MT-TDY",
        subject_code="ING",
        name_de="Thermodynamik",
        name_en="Thermodynamics",
        semester=4,
        credits=5,
        description_de="Hauptsätze, Wärmeübertragung, Anwendungen in der Medizintechnik",
        description_en="Laws of thermodynamics, heat transfer, applications in medical engineering",
        prerequisites=["MT-P1", "MT-M2"],
        units=[
            "Temperatur, Wärme, innere Energie",
            "1. und 2. Hauptsatz",
            "Wärmeleitung, Konvektion, Strahlung",
            "Thermische Gleichgewichte",
            "Medizintechnische Anwendungen (Kryotherapie, Inkubatoren)",
        ],
    ),
    ModuleDef(
        code="MT-QRA",
        subject_code="REG",
        name_de="Qualitätsmanagement & Regulatory Affairs",
        name_en="Quality Management & Regulatory Affairs",
        semester=4,
        credits=5,
        description_de="EU-MDR 2017/745, ISO 13485, ISO 14971, CE-Kennzeichnung, Risikoanalyse",
        description_en="EU MDR 2017/745, ISO 13485, ISO 14971, CE marking, risk analysis",
        units=[
            "Medizinprodukterecht (EU-MDR 2017/745)",
            "Produktklassifizierung & Konformitätsbewertung",
            "ISO 13485: Qualitätsmanagementsystem",
            "ISO 14971: Risikomanagement",
            "CE-Kennzeichnung & Technische Dokumentation",
        ],
    ),

    # ── SEMESTER 5 ──────────────────────────────────────────────────
    ModuleDef(
        code="MT-BVM",
        subject_code="MESS",
        name_de="Bildgebende Verfahren in der Medizin",
        name_en="Medical Imaging",
        semester=5,
        credits=5,
        description_de="Röntgen, CT, MRT, Ultraschall, Nuklearmedizin",
        description_en="X-ray, CT, MRI, ultrasound, nuclear medicine",
        prerequisites=["MT-P2", "MT-SYS"],
        units=[
            "Röntgenphysik & konventionelles Röntgen",
            "Computertomographie (CT)",
            "Magnetresonanztomographie (MRT)",
            "Ultraschallbildgebung",
            "Nuklearmedizin (PET, SPECT)",
        ],
    ),
    ModuleDef(
        code="MT-MGS",
        subject_code="MESS",
        name_de="Medizinische Geräte- & Sensortechnik",
        name_en="Medical Device & Sensor Technology",
        semester=5,
        credits=5,
        description_de="Biosensoren, EKG/EEG/EMG, Patientenmonitoring, Beatmungsgeräte",
        description_en="Biosensors, ECG/EEG/EMG, patient monitoring, ventilators",
        prerequisites=["MT-MS", "MT-EL1"],
        units=[
            "Bioelektrische Signale (EKG, EEG, EMG)",
            "Biosensoren & Labordiagnostik",
            "Patientenmonitoring-Systeme",
            "Beatmungs- & Narkosegeräte",
            "Elektrochirurgie & Defibrillation",
        ],
    ),
    ModuleDef(
        code="MT-MSW",
        subject_code="INF",
        name_de="Medizinische Softwaretechnik + Praktikum",
        name_en="Medical Software Engineering + Lab",
        semester=5,
        credits=5,
        description_de="Software als Medizinprodukt, IEC 62304, Usability (IEC 62366), DICOM, HL7/FHIR",
        description_en="Software as medical device, IEC 62304, usability (IEC 62366), DICOM, HL7/FHIR",
        prerequisites=["MT-INF2", "MT-QRA"],
        units=[
            "Software als Medizinprodukt (SaMD)",
            "IEC 62304: Software-Lebenszyklus",
            "IEC 62366: Usability Engineering",
            "DICOM & HL7/FHIR",
            "Praktikum: SaMD-Entwicklungsprojekt",
        ],
    ),
    ModuleDef(
        code="MT-RT",
        subject_code="MESS",
        name_de="Regelungstechnik",
        name_en="Control Engineering",
        semester=5,
        credits=5,
        description_de="Regelkreise, PID-Regler, Stabilität, Zustandsraum",
        description_en="Control loops, PID controllers, stability, state space",
        prerequisites=["MT-SYS", "MT-M4"],
        units=[
            "Offene und geschlossene Regelkreise",
            "PID-Regler: Entwurf & Einstellung",
            "Stabilität (Hurwitz, Nyquist, Bode)",
            "Zustandsraumbeschreibung",
            "Medizintechnische Regelungssysteme (Infusionspumpen, Beatmung)",
        ],
    ),
    ModuleDef(
        code="MT-BME",
        subject_code="ING",
        name_de="Biomechanik",
        name_en="Biomechanics",
        semester=5,
        credits=5,
        description_de="Bewegungsanalyse, Gelenkbelastung, Prothesen, FEM, Implantate",
        description_en="Motion analysis, joint loading, prosthetics, FEM, implants",
        prerequisites=["MT-TM1", "MT-HB2"],
        units=[
            "Biomechanische Grundlagen",
            "Ganganalyse & Bewegungserfassung",
            "Gelenkbelastung & Implantate",
            "Finite-Elemente-Methode (FEM, Einführung)",
            "Prothesen & Orthesen",
        ],
    ),
    ModuleDef(
        code="MT-PM",
        subject_code="MGMT",
        name_de="Projektmanagement",
        name_en="Project Management",
        semester=5,
        credits=5,
        description_de="Agile & klassische Methoden, Kosten, Teamführung, Design Thinking",
        description_en="Agile & classical methods, cost, team leadership, design thinking",
        prerequisites=["MT-IAW"],
        units=[
            "Klassisches PM (Wasserfall, V-Modell)",
            "Agiles PM (Scrum, Kanban)",
            "Kostenplanung & Ressourcenmanagement",
            "Teamführung & Kommunikation",
            "Design Thinking & Innovation",
        ],
    ),

    # ── SEMESTER 6 (Praxissemester) ─────────────────────────────────
    ModuleDef(
        code="MT-PX",
        subject_code="PRAXIS",
        name_de="Praxismodul (Industriepraktikum, 20 Wochen)",
        name_en="Internship Module (Industrial Placement, 20 weeks)",
        semester=6,
        credits=30,
        description_de="20-wöchiges Praktikum in einem Unternehmen der Medizintechnik-Branche",
        description_en="20-week internship in a medical technology company",
        prerequisites=[
            "MT-M4", "MT-EL2", "MT-SYS", "MT-QRA",
            "MT-HB2", "MT-INF3",
        ],
        units=[
            "Orientierungsphase im Unternehmen",
            "Mitarbeit an realen Projekten",
            "Anwendung ingenieurwiss. Methoden",
            "Dokumentation & Reflexion",
            "Praxisbericht & Präsentation",
        ],
    ),

    # ── SEMESTER 7 (Abschluss) ──────────────────────────────────────
    ModuleDef(
        code="MT-WPF1",
        subject_code="PRAXIS",
        name_de="Wahlpflichtfach 1 (Schwerpunkt)",
        name_en="Elective 1 (Specialization)",
        semester=7,
        credits=5,
        description_de="Vertiefungsmodul aus dem gewählten Schwerpunkt (Mess-/Gerätetechnik, Biomechanik, Datensysteme)",
        description_en="Advanced module from chosen specialization area",
        units=[
            "Schwerpunktspezifische Vertiefung",
            "Aktuelle Forschungsthemen",
            "Seminararbeit / Projektarbeit",
        ],
    ),
    ModuleDef(
        code="MT-WPF2",
        subject_code="PRAXIS",
        name_de="Wahlpflichtfach 2 (Schwerpunkt)",
        name_en="Elective 2 (Specialization)",
        semester=7,
        credits=5,
        description_de="Zweites Vertiefungsmodul aus Schwerpunkt oder fachübergreifende Vertiefung",
        description_en="Second advanced module from specialization or interdisciplinary topic",
        units=[
            "Schwerpunktspezifische Vertiefung",
            "Interdisziplinärer Ansatz",
            "Seminararbeit / Projektarbeit",
        ],
    ),
    ModuleDef(
        code="MT-SEM",
        subject_code="PRAXIS",
        name_de="Seminar",
        name_en="Seminar",
        semester=7,
        credits=5,
        description_de="Wissenschaftliches Seminar mit Vortrag und Diskussion aktueller Forschung",
        description_en="Academic seminar with presentation and discussion of current research",
        prerequisites=["MT-IAW"],
        units=[
            "Literaturstudium",
            "Ausarbeitung des Seminarvortrags",
            "Vortrag & wissenschaftliche Diskussion",
        ],
    ),
    ModuleDef(
        code="MT-BA",
        subject_code="PRAXIS",
        name_de="Bachelorarbeit + Kolloquium",
        name_en="Bachelor Thesis + Colloquium",
        semester=7,
        credits=15,
        description_de="Selbstständige Bearbeitung eines medizintechnischen Themas, Kolloquium",
        description_en="Independent treatment of a biomedical engineering topic, colloquium",
        prerequisites=["MT-PX"],
        units=[
            "Themenfindung & Exposé",
            "Literaturrecherche & Stand der Technik",
            "Durchführung & Ergebnisse",
            "Schriftliche Ausarbeitung",
            "Kolloquium (Vortrag & Verteidigung)",
        ],
    ),
]


# ──────────────────────────────────────────────────────────────────────
# Projekt-Komplexitäts-Level
# ──────────────────────────────────────────────────────────────────────

@dataclass
class ComplexityLevelDef:
    level: str
    name_de: str
    name_en: str
    description_de: str
    description_en: str
    example_products: list[str]
    required_module_codes: list[str]


COMPLEXITY_LEVELS: list[ComplexityLevelDef] = [
    ComplexityLevelDef(
        level="A",
        name_de="Einfaches Messgerät",
        name_en="Simple Measurement Device",
        description_de="Passives oder einfaches aktives Medizinprodukt mit wenigen Sensoren",
        description_en="Passive or simple active medical device with few sensors",
        example_products=[
            "Digitales Fieberthermometer",
            "Blutdruckmessgerät (nicht-invasiv)",
            "Pulsoximeter (Finger-Clip)",
            "Spirometer (einfach)",
        ],
        required_module_codes=[
            "MT-M1", "MT-M2", "MT-P1", "MT-ET1", "MT-ET2",
            "MT-INF1", "MT-HB1", "MT-MS", "MT-QRA", "MT-PM",
        ],
    ),
    ComplexityLevelDef(
        level="B",
        name_de="Signalverarbeitungssystem",
        name_en="Signal Processing System",
        description_de="Aktives Medizinprodukt mit komplexer Signalerfassung und -verarbeitung",
        description_en="Active medical device with complex signal acquisition and processing",
        example_products=[
            "EKG-Wearable",
            "EMG-Biofeedback-Gerät",
            "EEG-Schlafmonitor",
            "Langzeit-Blutdruckmonitor",
        ],
        required_module_codes=[
            "MT-M1", "MT-M2", "MT-M3", "MT-P1", "MT-P2",
            "MT-ET1", "MT-ET2", "MT-EL1", "MT-INF1", "MT-INF2",
            "MT-HB1", "MT-HB2", "MT-MS", "MT-SYS", "MT-MGS",
            "MT-QRA", "MT-PM",
        ],
    ),
    ComplexityLevelDef(
        level="C",
        name_de="Software-Medizinprodukt (SaMD)",
        name_en="Software as Medical Device (SaMD)",
        description_de="Software-basiertes Medizinprodukt (App, Diagnosesoftware, Telemedizin)",
        description_en="Software-based medical device (app, diagnostic software, telemedicine)",
        example_products=[
            "Diagnostik-App mit KI",
            "Telemedizin-Plattform",
            "Therapie-Begleit-App",
            "Medizinische Bild-Analyse-Software",
        ],
        required_module_codes=[
            "MT-M1", "MT-M2", "MT-STAT", "MT-INF1", "MT-INF2",
            "MT-INF3", "MT-MSW", "MT-HB1", "MT-HB2",
            "MT-QRA", "MT-PM", "MT-BVM",
        ],
    ),
    ComplexityLevelDef(
        level="D",
        name_de="Implantierbares / Therapeutisches Gerät",
        name_en="Implantable / Therapeutic Device",
        description_de="Komplexes Gerät: Implantate, Prothesen, Therapiegeräte",
        description_en="Complex device: implants, prostheses, therapy devices",
        example_products=[
            "Cochlea-Implantat (Prototyp)",
            "Myoelektrische Handprothese",
            "Neurostimulator",
            "Insulin-Pumpe (Prototyp)",
        ],
        required_module_codes=[
            "MT-M1", "MT-M2", "MT-M3", "MT-M4",
            "MT-P1", "MT-P2",
            "MT-ET1", "MT-ET2", "MT-EL1", "MT-EL2",
            "MT-INF1", "MT-INF2", "MT-INF3", "MT-MSW",
            "MT-HB1", "MT-HB2", "MT-ZMB",
            "MT-TM1", "MT-BME",
            "MT-MS", "MT-SYS", "MT-MGS", "MT-RT",
            "MT-QRA", "MT-PM",
        ],
    ),
    ComplexityLevelDef(
        level="E",
        name_de="Komplexes Gesamtsystem",
        name_en="Complex Integrated System",
        description_de="Großgeräte, bildgebende Systeme, Laborautomatisierung — alle Module nötig",
        description_en="Large-scale devices, imaging systems, lab automation — all modules required",
        example_products=[
            "MRT-Spulen-Zubehör",
            "Roboter-assistiertes Chirurgie-Modul",
            "Laborautomatisierungs-System",
            "Multisensor-Intensivstations-Monitor",
        ],
        required_module_codes=[m.code for m in MODULES if m.semester <= 5],
    ),
]


# ──────────────────────────────────────────────────────────────────────
# Helper: Prerequisite-Graph
# ──────────────────────────────────────────────────────────────────────

def get_prerequisite_graph() -> dict[str, list[str]]:
    """Return {module_code: [prerequisite_codes]} for all modules."""
    return {m.code: m.prerequisites for m in MODULES if m.prerequisites}


def get_modules_by_semester() -> dict[int, list[ModuleDef]]:
    """Return {semester: [modules]} grouped by semester."""
    result: dict[int, list[ModuleDef]] = {}
    for m in MODULES:
        result.setdefault(m.semester, []).append(m)
    return result


def get_subject_lookup() -> dict[str, SubjectDef]:
    """Return {subject_code: SubjectDef}."""
    return {s.code: s for s in SUBJECTS}


def get_module_lookup() -> dict[str, ModuleDef]:
    """Return {module_code: ModuleDef}."""
    return {m.code: m for m in MODULES}
