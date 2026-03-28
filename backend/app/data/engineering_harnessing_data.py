"""
Engineering Harnessing Seed Data — Part A
L02 Tech Units & Chains, L09 Stage Gates, L12 Quality Metrics,
L13 Impact Assessments & Surveys, L04 Mnemonics.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ─────────────────────────────────────────────────────────────────────────────
# Dataclass definitions (used by seed_content.py)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TechUnitDef:
    level: str                   # "A"–"E"
    name_de: str
    name_en: str
    description_de: str
    description_en: str
    io_spec: dict
    limitations: str


@dataclass
class TechChainDef:
    level: str
    name: str
    description: str
    unit_names_en: list[str]     # ordered list matching TechUnitDef.name_en


@dataclass
class MnemonicDef:
    module_code: str
    unit_position: int           # 0-indexed within module.units list
    mnemonic_text: str
    mnemonic_type: str           # acronym | story | visual | rhyme | analogy
    language: str = "de"


@dataclass
class QuestionDef:
    module_code: str
    unit_position: int           # 0-indexed
    question_de: str
    question_en: str
    question_type: str           # multiple_choice | free_text | matching
    answer_options: dict | None
    correct_answer: dict
    difficulty: str              # easy | medium | hard
    bloom_level: str             # remember | understand | apply | analyze | evaluate | create


# ─────────────────────────────────────────────────────────────────────────────
# L02 — Tech Units
# ─────────────────────────────────────────────────────────────────────────────

TECH_UNITS: list[TechUnitDef] = [

    # ── Level A: Simple Measurement ──────────────────────────────────────────

    TechUnitDef(
        level="A",
        name_de="Temperatursensor NTC",
        name_en="Temperature Sensor NTC",
        description_de="Passiver Widerstandssensor (NTC-Thermistor) zur Temperaturerfassung im klinischen Bereich.",
        description_en="Passive NTC thermistor for clinical temperature measurement.",
        io_spec={"input": "thermal gradient (°C)", "output": "resistance (Ω) → voltage via voltage divider"},
        limitations="Bereich: −40 °C bis +150 °C; nicht-lineare Kennlinie erfordert Software-Linearisierung.",
    ),
    TechUnitDef(
        level="A",
        name_de="Blutdruckmanschette (nicht-invasiv)",
        name_en="Non-Invasive Blood Pressure Cuff",
        description_de="Oszillometrische NIBP-Manschette zur nicht-invasiven Blutdruckmessung.",
        description_en="Oscillometric NIBP cuff for non-invasive blood pressure monitoring.",
        io_spec={"input": "arterielle Pulsation (Arm)", "output": "systolischer/diastolischer Druck (mmHg)"},
        limitations="Genauigkeit abhängig von Ruheposition; Bewegungsartefakte verschlechtern Ergebnis.",
    ),
    TechUnitDef(
        level="A",
        name_de="Pulsoximetrie-Sonde (SpO₂)",
        name_en="Pulse Oximetry Probe (SpO2)",
        description_de="Nicht-invasiver optischer Sensor zur Messung der arteriellen Sauerstoffsättigung.",
        description_en="Non-invasive optical sensor for arterial oxygen saturation measurement.",
        io_spec={"input": "Dual-Wellenlängen-LED (660 nm / 940 nm)", "output": "SpO₂ (%) + Herzfrequenz (bpm)"},
        limitations="Ungenau bei Nagellack, Minderperfusion oder starker Umgebungsbeleuchtung.",
    ),
    TechUnitDef(
        level="A",
        name_de="LCD-Anzeigeeinheit",
        name_en="LCD Display Module",
        description_de="Alphanumerisches oder grafisches LCD-Modul zur Anzeige von Messwerten.",
        description_en="Alphanumeric or graphical LCD module for displaying measurement values.",
        io_spec={"input": "serielles/paralleles Datensignal (SPI/I²C/parallel)", "output": "alphanumerische oder grafische Anzeige"},
        limitations="Begrenzte Bildwiederholrate; nicht geeignet für schnelle Wellenformdarstellung.",
    ),

    # ── Level B: Signal Processing ───────────────────────────────────────────

    TechUnitDef(
        level="B",
        name_de="EKG-Elektroden-Array (10-polig)",
        name_en="ECG Electrode Array (10-lead)",
        description_de="Klebende Ag/AgCl-Oberflächen­elektroden für 12-Kanal-EKG-Ableitungen.",
        description_en="Ag/AgCl surface electrodes for 12-lead ECG acquisition.",
        io_spec={"input": "bioelektrisches Oberflächenpotential (μV-Bereich)", "output": "12 differentielle Spannungskanäle"},
        limitations="Empfindlich gegen EMI; Hautvorbereitung erforderlich; Bewegungsartefakte.",
    ),
    TechUnitDef(
        level="B",
        name_de="Instrumentationsverstärker INA128",
        name_en="Instrumentation Amplifier INA128",
        description_de="Präzisions-InAmp mit einstellbarem Verstärkungsfaktor und CMRR > 100 dB.",
        description_en="Precision instrumentation amplifier with adjustable gain and CMRR > 100 dB.",
        io_spec={"input": "Differenzspannung (μV–mV)", "output": "verstärktes Signal (mV–V)"},
        limitations="Verstärkung durch externen Widerstand eingestellt; Versorgungsrauschen wirkt sich aus.",
    ),
    TechUnitDef(
        level="B",
        name_de="Analoges Bandpassfilter (0,05–150 Hz)",
        name_en="Analog Bandpass Filter (0.05–150 Hz)",
        description_de="Aktives Butterworth-Bandpassfilter zur EKG-Signalkonditionierung.",
        description_en="Active Butterworth bandpass filter for ECG signal conditioning.",
        io_spec={"input": "breitbandiges analoges Signal", "output": "bandbegrenztes Signal (EKG-Band 0,05–150 Hz)"},
        limitations="Feste Grenzfrequenzen; Phasenverzerrung an den Bandgrenzen.",
    ),
    TechUnitDef(
        level="B",
        name_de="16-bit ADC (Σ-Δ-Wandler)",
        name_en="16-bit ADC (Sigma-Delta Converter)",
        description_de="Hochauflösender Sigma-Delta-ADC für die Digitalisierung biomedizinischer Signale.",
        description_en="High-resolution sigma-delta ADC for digitizing biomedical signals.",
        io_spec={"input": "Analogspannung (0–3,3 V)", "output": "16-bit Digitalwort bei ≤ 10 ksps"},
        limitations="Wandlungslatenz; Anti-Aliasing-Filter vorgeschaltet; Masserauschen sensitiv.",
    ),
    TechUnitDef(
        level="B",
        name_de="DSP-Prozessor (ARM Cortex-M4)",
        name_en="DSP Processor (ARM Cortex-M4)",
        description_de="Mikrocontroller mit Hardware-FPU und DSP-Instruktionen für Echtzeitverarbeitung.",
        description_en="Microcontroller with hardware FPU and DSP instructions for real-time processing.",
        io_spec={"input": "digitale Samples via SPI/UART", "output": "gefilterte Signale, FFT-Ergebnisse, Parameterdaten"},
        limitations="Echtzeit-Constraints; begrenzter RAM für große FIR-Kernel.",
    ),

    # ── Level C: Software as Medical Device ──────────────────────────────────

    TechUnitDef(
        level="C",
        name_de="HL7/FHIR-Integrations-Gateway",
        name_en="HL7/FHIR Integration Gateway",
        description_de="Middleware-Komponente zur Übersetzung proprietärer Gerätedaten in FHIR R4-Ressourcen.",
        description_en="Middleware component translating proprietary device data to FHIR R4 resources.",
        io_spec={"input": "proprietäre Gerätedaten (JSON/HL7 v2.x)", "output": "FHIR R4-Ressourcen via REST-API"},
        limitations="Mapping-Profile erforderlich; Interoperabilität nach IHE-Profilen validieren.",
    ),
    TechUnitDef(
        level="C",
        name_de="Klinische Cloud-Datenbank (PostgreSQL + Audit)",
        name_en="Clinical Cloud Database (PostgreSQL + Audit Trail)",
        description_de="DSGVO-konforme PostgreSQL-Datenbank mit unveränderlichem Audit-Log für klinische Daten.",
        description_en="GDPR-compliant PostgreSQL database with immutable audit trail for clinical data.",
        io_spec={"input": "strukturierte klinische Daten (FHIR/HL7)", "output": "abfragbare Patientendaten, Audit-Logs"},
        limitations="DSGVO-Compliance erforderlich; strenge Zugriffskontrolle (RBAC) obligatorisch.",
    ),
    TechUnitDef(
        level="C",
        name_de="KI-Inferenz-Engine (CNN/Transformer)",
        name_en="AI Inference Engine (CNN/Transformer)",
        description_de="Deep-Learning-Modell zur Klassifikation oder Regression klinischer Messdaten.",
        description_en="Deep learning model for classification or regression of clinical measurement data.",
        io_spec={"input": "normalisierte Sensordaten oder medizinische Bilder", "output": "Klassifikationsergebnis + Konfidenzwert"},
        limitations="Black-Box; XAI für MDR Klasse IIb+ erforderlich; Modell-Drift-Monitoring nötig.",
    ),
    TechUnitDef(
        level="C",
        name_de="Klinisches Entscheidungsunterstützungs-UI",
        name_en="Clinical Decision Support UI",
        description_de="Benutzeroberfläche für klinisches Personal zur Visualisierung von Analyseergebnissen.",
        description_en="User interface for clinical staff to visualize analysis results and alerts.",
        io_spec={"input": "strukturierte Analyseergebnisse (JSON)", "output": "klinisches Dashboard (Web/Mobile)"},
        limitations="IEC 62366 Usability Testing erforderlich; WCAG 2.1 AA Barrierefreiheit.",
    ),

    # ── Level D: Implantable Device ───────────────────────────────────────────

    TechUnitDef(
        level="D",
        name_de="Biokompatibler Titangehäuse",
        name_en="Biocompatible Titanium Enclosure",
        description_de="Hermetisch versiegeltes Titangehäuse (Grad 23) für implantierbare Elektronik.",
        description_en="Hermetically sealed grade-23 titanium housing for implantable electronics.",
        io_spec={"input": "Elektronikkomponenten, Durchführungen (Feedthroughs)", "output": "IP68-Schutz, biokompatibles Gehäuse"},
        limitations="ISO 10993 Biokompatibilitätsprüfung erforderlich; Laserschweißen notwendig.",
    ),
    TechUnitDef(
        level="D",
        name_de="Platin-Iridium-Stimulationselektrode",
        name_en="Platinum-Iridium Stimulation Electrode",
        description_de="Biokompatible Stimulationselektrode aus Pt/Ir-Legierung für elektrische Gewebereizung.",
        description_en="Biocompatible Pt/Ir alloy stimulation electrode for electrical tissue stimulation.",
        io_spec={"input": "geregelte Stromimpulse (μA–mA)", "output": "ladungsbalancierte biphasische Gewebestimulation"},
        limitations="Ladungsdichtegrenzen (30 μC/cm²); Korrosionsbeständigkeit kritisch.",
    ),
    TechUnitDef(
        level="D",
        name_de="Li-Ion Medizinakku (ISO 14708)",
        name_en="Li-Ion Medical Battery (ISO 14708)",
        description_de="Primär- oder Sekundärzelle nach ISO 14708 für implantierbare medizinische Geräte.",
        description_en="Primary or secondary cell per ISO 14708 for implantable medical devices.",
        io_spec={"input": "Ladestrom (drahtlos/Kontakt)", "output": "geregelte Versorgungsspannung (3,0–4,2 V, 10–500 mAh)"},
        limitations="Lebensdauer 5–10 Jahre; temperatursensitiv; MRT-Konditionalität prüfen.",
    ),
    TechUnitDef(
        level="D",
        name_de="Telemetriemodul (MICS 402–405 MHz)",
        name_en="Wireless Telemetry Module (MICS 402–405 MHz)",
        description_de="Kurzstrecken-Funkmodul im MICS-Band für telemetrische Datenübertragung implantierbarer Geräte.",
        description_en="Short-range radio module in MICS band for telemetric data transfer of implantable devices.",
        io_spec={"input": "serialisierte klinische Daten", "output": "verschlüsselte HF-Übertragung (MICS-Band, ≤ 25 μW)"},
        limitations="Reichweite < 2 m; Duty-Cycle-Beschränkungen; FCC/CE-HF-Zertifizierung erforderlich.",
    ),
    TechUnitDef(
        level="D",
        name_de="Energiesparender ARM-Mikrocontroller (Cortex-M0+)",
        name_en="Low-Power ARM Microcontroller (Cortex-M0+)",
        description_de="Ultra-Low-Power-Mikrokontroller für die Echtzeit-Therapiesteuerung in Implantaten.",
        description_en="Ultra-low-power microcontroller for real-time therapy control in implantable devices.",
        io_spec={"input": "Sensor-/Telemtrie-Daten, Programmierschnittstelle", "output": "Echtzeit-Steuersignale, Therapieabgabe"},
        limitations="Sleep-Modi kritisch für Langlebigkeit; kein FPU; strenge Timing-Anforderungen.",
    ),

    # ── Level E: Complex Integrated System ───────────────────────────────────

    TechUnitDef(
        level="E",
        name_de="Multimodales Sensor-Array",
        name_en="Multi-Modal Sensor Array",
        description_de="Synchronisiertes Array aus EKG-, SpO₂-, Temperatur-, Blutdruck- und Atemsensoren.",
        description_en="Synchronized array of ECG, SpO2, temperature, blood pressure, and respiratory sensors.",
        io_spec={"input": "physiologische Signale (EKG, SpO₂, Temp., Druck, Atmung)", "output": "synchronisierte Mehrkanalzeitreihe"},
        limitations="Synchronisationslatenz < 1 ms erforderlich; Kabelmanagement kritisch.",
    ),
    TechUnitDef(
        level="E",
        name_de="Echtzeit-Betriebssystem (FreeRTOS)",
        name_en="Real-Time Operating System (FreeRTOS)",
        description_de="RTOS mit deterministischem Task-Scheduling für sicherheitskritische medizinische Anwendungen.",
        description_en="RTOS with deterministic task scheduling for safety-critical medical applications.",
        io_spec={"input": "Task-Scheduling-Anfragen, Interrupts", "output": "deterministisches Echtzeit-Task-Management, ≤ 1 ms Latenz"},
        limitations="Priority Inversion muss behandelt werden; Stack-Overflow-Erkennung erforderlich.",
    ),
    TechUnitDef(
        level="E",
        name_de="Sicherheitsmonitor (IEC 61508 SIL-2)",
        name_en="Safety Monitor (IEC 61508 SIL-2)",
        description_de="Dedizierter Sicherheitsrechner zur Überwachung von Systemzuständen und Auslösung von Sicherheitszuständen.",
        description_en="Dedicated safety computer monitoring system states and triggering safe states.",
        io_spec={"input": "Systemzustand, Sensorbereiche, Watchdog-Signale", "output": "Safe-State-Kommandos, Alarmauslösung, Audit-Events"},
        limitations="Formale Verifikation erforderlich; diverse Redundanz für SIL-2-Nachweis.",
    ),
    TechUnitDef(
        level="E",
        name_de="CAN-Bus Klinisches Netzwerk",
        name_en="CAN Bus Clinical Network",
        description_de="Deterministisches Feldbus-Netzwerk nach ISO 11898 für die Kopplung klinischer Subsysteme.",
        description_en="Deterministic fieldbus network per ISO 11898 for coupling clinical subsystems.",
        io_spec={"input": "Geräteknoten (Subsysteme)", "output": "priorisierte Nachrichtenzustellung ≤ 1 Mbit/s"},
        limitations="Max. 110 Knoten; Bus-Terminierung erforderlich; EMV-Abschirmung notwendig.",
    ),
    TechUnitDef(
        level="E",
        name_de="Intelligente Energieverwaltungseinheit",
        name_en="Intelligent Power Management Unit",
        description_de="Mehrkanaliges Netzteil nach IEC 60601-1 mit Akku-Backup und Isolationswächter.",
        description_en="Multi-channel medical-grade power supply per IEC 60601-1 with battery backup.",
        io_spec={"input": "Netzspannung / Akku / PoE", "output": "geregelte isolierte Versorgungsschienen (3,3 V / 5 V / 12 V / ±15 V)"},
        limitations="IEC 60601-1 elektrische Sicherheit; Isolation ≥ 1500 V; Ableitstrom < 10 μA.",
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# L02 — Tech Chains
# ─────────────────────────────────────────────────────────────────────────────

TECH_CHAINS: list[TechChainDef] = [
    TechChainDef(
        level="A",
        name="Digitales Thermometer",
        description="Einfache Temperaturmessung: NTC-Sensor → Spannungsteiler → Mikrocontroller → LCD-Anzeige.",
        unit_names_en=["Temperature Sensor NTC", "LCD Display Module"],
    ),
    TechChainDef(
        level="A",
        name="Finger-Pulsoximeter",
        description="Nicht-invasive SpO₂-Messung mit optischem Sensor und visueller Ergebnisdarstellung.",
        unit_names_en=["Pulse Oximetry Probe (SpO2)", "LCD Display Module"],
    ),
    TechChainDef(
        level="B",
        name="12-Kanal-EKG-System",
        description="Vollständige EKG-Signalkette von der Elektrode über Verstärkung und Filterung bis zur digitalen Verarbeitung.",
        unit_names_en=[
            "ECG Electrode Array (10-lead)",
            "Instrumentation Amplifier INA128",
            "Analog Bandpass Filter (0.05–150 Hz)",
            "16-bit ADC (Sigma-Delta Converter)",
            "DSP Processor (ARM Cortex-M4)",
        ],
    ),
    TechChainDef(
        level="C",
        name="SaMD Diagnoseplattform",
        description="Software als Medizinprodukt: klinisches UI → FHIR-Interoperabilität → KI-Analyse → Datenbankpersistenz.",
        unit_names_en=[
            "Clinical Decision Support UI",
            "HL7/FHIR Integration Gateway",
            "AI Inference Engine (CNN/Transformer)",
            "Clinical Cloud Database (PostgreSQL + Audit Trail)",
        ],
    ),
    TechChainDef(
        level="D",
        name="Implantierbarer Herzschrittmacher",
        description="Vollständige Schrittmacher-Architektur: Gehäuse → Prozessor → Stimulationselektrode → Akku → Telemetrie.",
        unit_names_en=[
            "Biocompatible Titanium Enclosure",
            "Low-Power ARM Microcontroller (Cortex-M0+)",
            "Platinum-Iridium Stimulation Electrode",
            "Li-Ion Medical Battery (ISO 14708)",
            "Wireless Telemetry Module (MICS 402–405 MHz)",
        ],
    ),
    TechChainDef(
        level="E",
        name="Integriertes Intensivstationsmonitoring",
        description="Komplexes Patientenüberwachungssystem: Sensor-Array → RTOS → Sicherheitsmonitor → Netzwerk → Energieversorgung.",
        unit_names_en=[
            "Multi-Modal Sensor Array",
            "Real-Time Operating System (FreeRTOS)",
            "Safety Monitor (IEC 61508 SIL-2)",
            "CAN Bus Clinical Network",
            "Intelligent Power Management Unit",
        ],
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# L09 — Stage Gate Criteria (7 project stages)
# ─────────────────────────────────────────────────────────────────────────────

STAGE_GATE_DATA: list[dict] = [
    {
        "stage": "idea",
        "criteria": {
            "checklist": [
                "Medizinisches Problem klar definiert",
                "Zielgruppe (Patienten / Anwender) benannt",
                "Erste Marktrecherche durchgeführt",
                "Projektziel in einem Satz formulierbar",
            ],
            "min_score": 3,
        },
        "required_artifacts": ["project_brief"],
    },
    {
        "stage": "concept",
        "criteria": {
            "checklist": [
                "Anforderungsspezifikation (funktional & nicht-funktional) erstellt",
                "Erste Risikoanalyse (ISO 14971) durchgeführt",
                "Regulatory-Pfad (Produktklasse, Konformitätsverfahren) festgelegt",
                "Technologieauswahl begründet",
                "Vorläufige Zeitplanung vorhanden",
            ],
            "min_score": 4,
        },
        "required_artifacts": ["requirements_spec", "risk_analysis_v1"],
    },
    {
        "stage": "mvp",
        "criteria": {
            "checklist": [
                "Kernfunktion lauffähig implementiert",
                "Software-Architektur dokumentiert (IEC 62304)",
                "Unit-Tests für kritische Funktionen vorhanden",
                "Erste Nutzertests durchgeführt (Usability Formative, IEC 62366)",
                "Bekannte Mängel dokumentiert",
            ],
            "min_score": 4,
        },
        "required_artifacts": ["software_architecture", "test_report_v1", "usability_notes"],
    },
    {
        "stage": "2d",
        "criteria": {
            "checklist": [
                "2D-CAD-Zeichnungen / Schaltpläne vollständig",
                "Maßblatttoleranzen definiert",
                "Materialauswahl mit Biokompatibilitätsbegründung",
                "Elektrische Sicherheitsnachweis (IEC 60601-1) begonnen",
                "Designverifizierung durchgeführt",
            ],
            "min_score": 4,
        },
        "required_artifacts": ["cad_drawings_2d", "material_list", "design_verification_report"],
    },
    {
        "stage": "3d",
        "criteria": {
            "checklist": [
                "3D-Prototyp (FDM / SLA / Metall) gefertigt",
                "Montage- und Demontagetest durchgeführt",
                "Ergonomie / Handling bewertet",
                "EMV-Vortest (Bench-Test) bestanden",
                "Softwareintegration in Hardware getestet",
            ],
            "min_score": 4,
        },
        "required_artifacts": ["3d_model", "integration_test_report", "emv_pretest"],
    },
    {
        "stage": "real_world",
        "criteria": {
            "checklist": [
                "Klinische Studie / Anwendertest mit repräsentativen Nutzern abgeschlossen",
                "Summative Usability-Evaluation (IEC 62366) dokumentiert",
                "Leistungsnachweis (klinische Evaluation) erbracht",
                "Vollständige Technische Dokumentation (MDR Annex II/III) erstellt",
                "GSPR-Checkliste abgehakt",
            ],
            "min_score": 5,
        },
        "required_artifacts": [
            "clinical_evaluation_report",
            "usability_summative_report",
            "technical_documentation",
        ],
    },
    {
        "stage": "lifecycle",
        "criteria": {
            "checklist": [
                "Post-Market-Surveillance-Plan (PMS) implementiert",
                "Post-Market Clinical Follow-Up (PMCF) gestartet",
                "Vigilanz-Meldesystem eingerichtet",
                "Qualitätsmanagementsystem (ISO 13485) zertifiziert",
                "Regelmäßige PSUR / Periodic Safety Update Report vorgesehen",
            ],
            "min_score": 5,
        },
        "required_artifacts": [
            "pms_plan",
            "pmcf_plan",
            "vigilance_procedure",
            "qms_certificate",
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# L12 — Quality Metrics
# ─────────────────────────────────────────────────────────────────────────────

QUALITY_METRICS: list[dict] = [
    {
        "name": "content_coverage",
        "description": "Prozentsatz der Moduleinheiten mit veröffentlichten Lerninhalten.",
        "target_value": 100.0,
        "unit": "%",
    },
    {
        "name": "question_coverage",
        "description": "Prozentsatz der Module mit mindestens 4 Prüfungsfragen in der Fragedatenbank.",
        "target_value": 100.0,
        "unit": "%",
    },
    {
        "name": "api_response_time_p95",
        "description": "95. Perzentil der API-Antwortzeit über alle Endpunkte.",
        "target_value": 500.0,
        "unit": "ms",
    },
    {
        "name": "user_satisfaction_score",
        "description": "Durchschnittliche Nutzerzufriedenheit (Skala 1–5) aus Umfrageantworten.",
        "target_value": 4.0,
        "unit": "score (1–5)",
    },
    {
        "name": "exam_pass_rate",
        "description": "Anteil der Prüfungsversuche mit ≥ 60 % Score.",
        "target_value": 70.0,
        "unit": "%",
    },
    {
        "name": "mnemonic_effectiveness",
        "description": "Anteil der Nutzer, die nach Verwendung von Eselsbrücken eine subjektive Lernverbesserung berichten.",
        "target_value": 75.0,
        "unit": "%",
    },
    {
        "name": "code_test_coverage",
        "description": "Prozentsatz der Backend-Codezeilen durch automatisierte Tests abgedeckt.",
        "target_value": 80.0,
        "unit": "%",
    },
    {
        "name": "accessibility_score",
        "description": "axe-core Barrierefreiheitsbewertung des Frontends (0–100, Lighthouse).",
        "target_value": 90.0,
        "unit": "score (0–100)",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# L13 — Impact Assessments
# ─────────────────────────────────────────────────────────────────────────────

IMPACT_ASSESSMENTS: list[dict] = [
    {
        "title": "Datenschutz & DSGVO-Compliance",
        "category": "Privacy & Legal",
        "description": (
            "TakiOS verarbeitet personenbezogene Daten (Lernfortschritt, Prüfungsergebnisse, Nutzerpräferenzen). "
            "Eine Datenschutz-Folgenabschätzung gemäß Art. 35 DSGVO wurde durchgeführt."
        ),
        "risk_level": "medium",
        "mitigation": (
            "Datensparsamkeit (nur notwendige Daten erheben), Privacy-by-Design-Architektur, "
            "pseudonymisierte Speicherung, Recht auf Löschung implementiert, DPA geschlossen."
        ),
    },
    {
        "title": "Bildungswirksamkeit",
        "category": "Educational Impact",
        "description": (
            "Die Plattform soll nachweislich den Lernerfolg von Medizintechnik-Studierenden verbessern. "
            "Ohne empirische Validierung besteht das Risiko, dass Lernziele nicht erreicht werden."
        ),
        "risk_level": "low",
        "mitigation": (
            "Einbindung von Lehrstuhl-Feedback (Dr. Pishop, Udo Vanstevendaal), "
            "formative Tests während der Entwicklung, summative Evaluation mit Studierenden-Kohorte."
        ),
    },
    {
        "title": "Barrierefreiheit & Inklusion",
        "category": "Accessibility",
        "description": (
            "Studierende mit motorischen, visuellen oder kognitiven Einschränkungen müssen die Plattform "
            "barrierefrei nutzen können (WCAG 2.1 AA). Nicht-Erfüllung führt zu Ausschluss."
        ),
        "risk_level": "medium",
        "mitigation": (
            "Implementierung von High-Contrast-Modus, Screen-Reader-Unterstützung (ARIA), "
            "Tastaturnavigation, reduzierten Bewegungsanimationen; axe-core-Tests in CI/CD."
        ),
    },
    {
        "title": "Ökologische Nachhaltigkeit",
        "category": "Environmental",
        "description": (
            "Serverinfrastruktur und KI-Inferenz verbrauchen Energie. "
            "CO₂-Fußabdruck der Plattform sollte transparent gemacht werden."
        ),
        "risk_level": "low",
        "mitigation": (
            "Hosting auf erneuerbaren Energien (z. B. Hetzner Green Energy), "
            "KI-Anfragen nur bei explizitem Nutzer-Trigger, Caching von häufigen Anfragen."
        ),
    },
    {
        "title": "Ethischer KI-Einsatz",
        "category": "AI Ethics",
        "description": (
            "KI-generierte Eselsbrücken und automatisches Grading können Fehler enthalten oder "
            "Vorurteile reproduzieren. Studierende könnten falsche Inhalte unkritisch übernehmen."
        ),
        "risk_level": "high",
        "mitigation": (
            "Klare Kennzeichnung KI-generierter Inhalte, menschliche Überprüfung durch Lehrende, "
            "Konfidenzwerte bei automatischem Grading anzeigen, Feedback-Mechanismus für Korrekturen."
        ),
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# L13 — Surveys
# ─────────────────────────────────────────────────────────────────────────────

SURVEYS: list[dict] = [
    {
        "title": "Lernplattform-Zufriedenheitsumfrage",
        "questions": [
            "Wie zufrieden sind Sie insgesamt mit der TakiOS-Plattform? (1 = sehr unzufrieden, 5 = sehr zufrieden)",
            "Wie hilfreich fanden Sie die personalisierten Eselsbrücken für Ihr Lernen?",
            "Waren die Prüfungsfragen angemessen schwierig und praxisrelevant?",
            "Wie einfach war die Navigation durch die Lernmodule?",
            "Welche Funktionen sollten verbessert oder ergänzt werden?",
        ],
    },
    {
        "title": "Engineering Harnessing Evaluierung",
        "questions": [
            "Hat die Verknüpfung von Lerninhalten mit Tech-Units (Bauteilen) Ihr Verständnis verbessert?",
            "Hat das Stufenmodell (Level A–E) Ihnen geholfen, die Komplexität von Medizinprodukten einzuschätzen?",
            "Wie hilfreich war der Compliance-Leitfaden (MDR, IEC 62304) für Ihre Projektarbeit?",
            "Würden Sie TakiOS anderen Medizintechnik-Studierenden empfehlen? Warum?",
            "Welcher Aspekt des Engineering-Harness-Konzepts hat Ihnen am meisten geholfen?",
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# L04 — Mnemonics (Eselsbrücken)
# ─────────────────────────────────────────────────────────────────────────────
# module_code + unit_position (0-indexed) identifies which content entry to attach to.

MNEMONIC_DATA: list[MnemonicDef] = [
    # MATH — Lineare Algebra
    MnemonicDef(
        module_code="MT-M1",
        unit_position=0,
        mnemonic_text=(
            "**ZEILE mal SPALTE** — bei der Matrizenmultiplikation gilt: "
            "Zeile des linken × Spalte des rechten Operanden. "
            "Merke: Z×S wie 'Zahlen-Summe' — die Zeile wandert nach rechts, die Spalte nach unten."
        ),
        mnemonic_type="analogy",
    ),
    # MATH — Integration
    MnemonicDef(
        module_code="MT-M2",
        unit_position=0,
        mnemonic_text=(
            "**Fläche unter der Kurve** — das bestimmte Integral ist nichts anderes als die Fläche, "
            "die eine Funktion mit der x-Achse einschließt. "
            "Stell dir vor, du schüttest Sand unter den Graphen — die Sandmenge ist das Integral."
        ),
        mnemonic_type="visual",
    ),
    # ET — Kirchhoff
    MnemonicDef(
        module_code="MT-ET1",
        unit_position=1,
        mnemonic_text=(
            "**KCL: Was rein kommt, muss raus** — der Knotensatz (KCL) bedeutet, "
            "dass an einem Knoten genauso viel Strom ankommt wie abfließt. "
            "Wie ein Wasserrohr: was hinein fließt, muss auch heraus. "
            "KVL: Im Rundgang summieren sich alle Spannungen zu null — wie beim Bergwandern: "
            "nach der Runde bist du wieder auf Ausgangshöhe."
        ),
        mnemonic_type="analogy",
    ),
    # ET — RC-Schaltungen
    MnemonicDef(
        module_code="MT-ET2",
        unit_position=2,
        mnemonic_text=(
            "**τ = R × C** — die Zeitkonstante tau sagt dir, wie schnell ein Kondensator lädt. "
            "Nach einer τ ist der Kondensator auf 63 % geladen, nach 5τ praktisch voll. "
            "Merke: **T**au = **R**esistor mal **C**apacitor = 'Trage Rucksack Camping' — "
            "je schwerer der Rucksack (R) und je größer die Tasche (C), desto länger brauchst du."
        ),
        mnemonic_type="acronym",
    ),
    # MED — Herzreizleitung
    MnemonicDef(
        module_code="MT-HB1",
        unit_position=3,
        mnemonic_text=(
            "**SA → AV → His → Tawara → Purkinje** — die Erregungsleitung des Herzens. "
            "Merksatz: **S**inus **A**nfang **H**alt **T**ief **P**umpt. "
            "Sinusknoten startet, AV-Knoten verzögert, His-Bündel leitet, "
            "Tawara-Schenkel verteilen, Purkinje-Fasern aktivieren den Ventrikel."
        ),
        mnemonic_type="acronym",
    ),
    # MED — Blutdruck
    MnemonicDef(
        module_code="MT-HB1",
        unit_position=4,
        mnemonic_text=(
            "**S/D = Systolisch über Diastolisch** — wie ein Bruch: "
            "oben (Zähler) = systolisch = Herz pumpt (System unter Druck), "
            "unten (Nenner) = diastolisch = Herz entspannt (Ruhe). "
            "Normalwert: 120/80 mmHg — 'zwölf achtzig wie im Ziel'."
        ),
        mnemonic_type="acronym",
    ),
    # PHYS — Schwingungen
    MnemonicDef(
        module_code="MT-P1",
        unit_position=3,
        mnemonic_text=(
            "**Federball-Analogie** — eine Schwingung ist wie ein Federball: "
            "Rückstellkraft F = −k·x (Feder zieht zurück), "
            "Masse m gibt Trägheit (Widerstand gegen Beschleunigung). "
            "ω = √(k/m): Steife Feder + leichte Masse = hohe Frequenz, wie eine dünne Gitarrensaite."
        ),
        mnemonic_type="analogy",
    ),
    # REG — MDR Klassen
    MnemonicDef(
        module_code="MT-QRA",
        unit_position=1,
        mnemonic_text=(
            "**MDR-Klassen: I II IIa IIb III** — Merksatz: 'Ich Irre Immer In Intensiv'. "
            "Klasse I: kein/minimales Risiko (Pflaster, Stethoskop). "
            "Klasse IIa: mittleres Risiko, kurzer Kontakt (Hörgerät). "
            "Klasse IIb: mittleres Risiko, langer Kontakt (Beatmungsgerät). "
            "Klasse III: höchstes Risiko, lebenswichtig (Herzschrittmacher, Gefäßstent)."
        ),
        mnemonic_type="story",
    ),
    # INF — Git Workflow
    MnemonicDef(
        module_code="MT-INF2",
        unit_position=3,
        mnemonic_text=(
            "**ACK-Push: Add, Commit, Push** — der Git-Workflow in drei Schritten: "
            "'**A**lle Änderungen **C**ommitten, dann **K**ommunizieren (Push)'. "
            "git add → Änderungen bereitstellen, "
            "git commit -m '...' → Schnappschuss erstellen, "
            "git push → zum Remote-Repository hochladen."
        ),
        mnemonic_type="acronym",
    ),
    # MESS — Nyquist-Shannon
    MnemonicDef(
        module_code="MT-SYS",
        unit_position=2,
        mnemonic_text=(
            "**Zweimal abtasten reicht** — das Nyquist-Shannon-Abtasttheorem besagt: "
            "Die Abtastfrequenz muss mindestens doppelt so groß sein wie die höchste Signalfrequenz. "
            "fs ≥ 2 · fmax. Merke: 'Nyquist sagt: Zwei ist genug — einmal für Plus, einmal für Minus.'"
        ),
        mnemonic_type="rhyme",
    ),
    # ING — Bernoulli
    MnemonicDef(
        module_code="MT-STR",
        unit_position=1,
        mnemonic_text=(
            "**Schnell = leicht, langsam = schwer** — das Bernoulli-Prinzip: "
            "Wo Fluid schnell strömt, ist der Druck niedrig; wo es langsam strömt, ist er hoch. "
            "Medizinisch: Verengung im Blutgefäß → Blut beschleunigt → Druckabfall (Stenose). "
            "Wie auf der Autobahn: enge Spur = schnell = wenig Platz zum Parken."
        ),
        mnemonic_type="analogy",
    ),
    # NAWI — pH-Wert
    MnemonicDef(
        module_code="MT-CH",
        unit_position=2,
        mnemonic_text=(
            "**pH = −log[H⁺]** — das 'p' steht für 'Potenz' (Potentia). "
            "pH 7 = neutral; pH < 7 = sauer (mehr H⁺-Ionen); pH > 7 = basisch (weniger H⁺). "
            "Merke: 'Saure Zitrone hat kleinen pH, Seifenwasser hat großen pH.' "
            "Blut-pH: 7,35–7,45 — außerhalb dieses Fensters = medizinischer Notfall."
        ),
        mnemonic_type="acronym",
    ),
    # MSW — IEC 62304 Software-Klassen
    MnemonicDef(
        module_code="MT-MSW",
        unit_position=1,
        mnemonic_text=(
            "**ABC der Softwareklassen (IEC 62304):** "
            "**A** = Harmlos (kein Schaden möglich), "
            "**B** = Bedenklich (nicht lebensbedrohlich), "
            "**C** = Critical (Tod oder schwere Verletzung möglich). "
            "Merksatz: 'A-software: Alles gut. B-software: Besser aufpassen. C-software: Chefsache!' "
            "Klasse bestimmt den Umfang der Dokumentation und Tests."
        ),
        mnemonic_type="story",
    ),
    # SYS — Fourier-Transformation
    MnemonicDef(
        module_code="MT-SYS",
        unit_position=1,
        mnemonic_text=(
            "**Jedes Signal = Summe von Sinuswellen** — die Fourier-Transformation zerlegt jedes "
            "periodische Signal in seine Frequenzanteile. "
            "Wie ein Prisma Licht in Spektralfarben aufteilt, teilt Fourier ein Signal in Frequenzen. "
            "Für medizinische Signale: EKG enthält Grundwelle (1 Hz) + Obertöne bis 150 Hz."
        ),
        mnemonic_type="analogy",
    ),
    # RT — PID-Regler
    MnemonicDef(
        module_code="MT-RT",
        unit_position=1,
        mnemonic_text=(
            "**P reagiert, I erinnert, D ahnt voraus** — die drei PID-Anteile: "
            "**P** (Proportional): reagiert auf den aktuellen Fehler — sofortiger Ausgleich. "
            "**I** (Integral): summiert vergangene Fehler auf — korrigiert bleibende Regelabweichung. "
            "**D** (Differential): sieht die Änderungsrate voraus — dämpft Überschwingen. "
            "Merke: PID = 'Patient Im Dienst' — der Regler arbeitet ständig für das Ziel."
        ),
        mnemonic_type="acronym",
    ),
]
