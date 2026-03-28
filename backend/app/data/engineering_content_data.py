"""Medizintechnik-Lerninhalt — Seed-Daten für TakiOS.

Echte Fachinhalte für das Curriculum Medizintechnik, HAW Hamburg.
Abdeckung: Biologie, Elektronik, Signalverarbeitung, Regulatorik, Bildgebung.
"""

CONTENT_DATA: dict[str, list[dict[str, str]]] = {
    # ──────────────────────────────────────────────────────────────
    # 1. Zelle — Aufbau und Funktion
    # ──────────────────────────────────────────────────────────────
    "zelle_aufbau": [
        {
            "title_de": "Die Zelle: Aufbau und Funktion",
            "title_en": "The Cell: Structure and Function",
            "body_de": """\
## Zellmembran und Membranpotenzial

Die Zellmembran besteht aus einer Phospholipid-Doppelschicht mit eingelagerten Proteinen
(Fluid-Mosaic-Modell, Singer & Nicolson 1972). Die amphiphilen Phospholipide orientieren
sich so, dass ihre hydrophoben Fettsäureketten nach innen zeigen und die hydrophilen
Kopfgruppen den wässrigen Extra- und Intrazellularraum berühren.

Das **Ruhemembranpotenzial** einer typischen Körperzelle beträgt −70 mV (Nerv) bis −90 mV
(Herzmuskel). Es entsteht durch unterschiedliche Ionenkonzentrationen auf beiden Seiten der
Membran sowie durch selektiv permeable Ionenkanäle:

| Ion | Extrazellulär (mM) | Intrazellulär (mM) |
|-----|-------------------|-------------------|
| Na⁺ | 145 | 12 |
| K⁺ | 4 | 155 |
| Cl⁻ | 120 | 4 |
| Ca²⁺ | 1,5 | 0,0001 |

Die Na⁺/K⁺-ATPase pumpt aktiv 3 Na⁺ nach außen und 2 K⁺ nach innen (elektrogen).
Das Gibbs-Donnan-Gleichgewicht und die Nernst-Gleichung beschreiben die Gleichgewichtspotenziale
einzelner Ionen:

$$E_{Ion} = \\frac{RT}{zF} \\ln\\frac{[Ion]_{extrazellulär}}{[Ion]_{intrazellulär}}$$

## Zellorganellen und ihre Funktion

Der **Zellkern** enthält die genomische DNA und ist von einer Doppelmembran (Kernhülle)
mit Kernporen umgeben. Er steuert die Genexpression.  
Das **Endoplasmatische Retikulum (ER)** existiert in rauer (Proteinsynthese) und glatter
(Lipidsynthese, Entgiftung) Form. **Ribosomen** übersetzen mRNA in Proteine.  
Der **Golgi-Apparat** modifiziert, sortiert und verpackt Proteine für ihre Bestimmungsorte.  
**Mitochondrien** (Doppelmembran, eigene DNA) sind die Kraftwerke der Zelle. In der
Atmungskette wird Glukose über Acetyl-CoA, Citratzyklus und oxidative Phosphorylierung
zu ATP, CO₂ und H₂O oxidiert:

$$C_6H_{12}O_6 + 6O_2 \\rightarrow 6CO_2 + 6H_2O + 36{-}38\\,ATP$$

**Lysosomen** enthalten Hydrolasen bei pH 4,5–5 für den intrazellulären Abbau von
Makromolekülen (Autophagie, Phagozytose).

## Relevanz für die Medizintechnik

Biopotenziale — Aktionspotenziale, EKG, EEG, EMG — entstehen durch koordinierte
Ionenstromänderungen in erregbaren Zellen. Jede elektrische Messung am Patienten misst
letztlich Ionenbewegungen, die über Gewebsimpedanzen elektrische Felder erzeugen.
Biosensoren (z. B. ionenselektive Elektroden, Mikroelektroden-Arrays) nutzen elektrochemische
Prinzipien dieser Membranphysik direkt aus.
""",
            "body_en": """\
## Cell Membrane and Membrane Potential

The cell membrane consists of a phospholipid bilayer with embedded proteins
(fluid-mosaic model, Singer & Nicolson 1972). The amphiphilic phospholipids orient so
that their hydrophobic fatty-acid tails face inward and the hydrophilic head groups face
the aqueous extra- and intracellular spaces.

The **resting membrane potential** of a typical body cell is −70 mV (nerve) to −90 mV
(cardiac muscle). It results from different ion concentrations on both sides of the membrane
and from selectively permeable ion channels.

The Nernst equation gives the equilibrium potential for a single ion:

$$E_{Ion} = \\frac{RT}{zF} \\ln\\frac{[Ion]_{extracellular}}{[Ion]_{intracellular}}$$

## Organelles and Their Functions

The **nucleus** contains genomic DNA surrounded by a double membrane (nuclear envelope)
with nuclear pores. The **endoplasmic reticulum (ER)** exists in rough (protein synthesis)
and smooth (lipid synthesis, detoxification) forms. **Mitochondria** (double membrane, own
DNA) are the powerhouses of the cell, producing ATP via the citric acid cycle and oxidative
phosphorylation:

$$C_6H_{12}O_6 + 6O_2 \\rightarrow 6CO_2 + 6H_2O + 36{-}38\\,ATP$$

## Relevance for Medical Device Engineering

Biopotentials — action potentials, ECG, EEG, EMG — arise from coordinated ion-current
changes in excitable cells. Every electrical measurement on a patient ultimately measures
ion movements that generate electric fields through tissue impedances. Biosensors such as
ion-selective electrodes and microelectrode arrays directly exploit the electrochemical
principles of membrane physics.
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 2. Herz-Kreislauf-System
    # ──────────────────────────────────────────────────────────────
    "herz_kreislauf": [
        {
            "title_de": "Herz-Kreislauf-System",
            "title_en": "Cardiovascular System",
            "body_de": """\
## Anatomie und Hämodynamik

Das Herz besteht aus vier Kammern: rechter Vorhof (RA), rechter Ventrikel (RV), linker
Vorhof (LA) und linker Ventrikel (LV). Der Körperkreislauf (Hochdruck, ~120/80 mmHg) und
der Lungenkreislauf (Niederdruck, ~25/10 mmHg) sind in Serie geschaltet.

Das **Herzminutenvolumen** (HZV) berechnet sich als:

$$HZV = Schlagvolumen \\times Herzfrequenz$$

Typisch: 70 mL × 70/min = 4,9 L/min. Der Frank-Starling-Mechanismus beschreibt, dass das
Schlagvolumen mit der enddiastolischen Füllung zunimmt (Kraft–Längen-Beziehung des
Myokards).

## Erregungsbildung und -leitung

1. **Sinusknoten** (60–100/min) → spontane Depolarisation (Schrittmacherpotenzial)
2. **AV-Knoten** → Verzögerung ~120 ms (diastolische Füllungszeit)
3. **His-Bündel → Tawara-Schenkel → Purkinje-Fasern** → gleichmäßige Ventrikelaktivierung

Störungen: AV-Block I–III, Schenkelblock, Vorhofflimmern (irregulär-irregular, fehlende
P-Wellen im EKG).

## Blutdruck und Gefäßphysiologie

Der arterielle Druck folgt dem Ohmschen Gesetz für Strömungen:

$$\\Delta P = HZV \\times R_{peripher}$$

Der **Windkessel-Effekt** der Aorta wandelt das intermittierende Herzpumpen in einen
nahezu kontinuierlichen Fluss um. Arteriolen sind die Hauptwiderstands­gefäße
(glatte Muskulatur, sympathisch innerviert).

## Klinische Messtechnik

Blutdruckmessgeräte (NIBP): Korotkoff-Phasen bei auskultatorischer Methode,
Oszillometrie bei automatischer Messung. Herzecho (Echokardiographie): Doppler-Effekt
zur Flussmessung, 2D/3D-B-Mode zur Anatomie. Implantierbare Herzschrittmacher (ICD/CRT)
müssen nach IEC 60601-2-27 geprüft werden.
""",
            "body_en": """\
## Anatomy and Haemodynamics

The heart consists of four chambers: right atrium (RA), right ventricle (RV), left atrium
(LA) and left ventricle (LV). The systemic circulation (high-pressure, ~120/80 mmHg) and
the pulmonary circulation (low-pressure, ~25/10 mmHg) are connected in series.

**Cardiac output (CO)** is calculated as:

$$CO = Stroke Volume \\times Heart Rate$$

Typical: 70 mL × 70 bpm = 4.9 L/min. The Frank–Starling mechanism states that stroke
volume increases with end-diastolic volume (force–length relationship of the myocardium).

## Impulse Formation and Conduction

1. **Sinoatrial node** (60–100 bpm) → spontaneous depolarisation (pacemaker potential)
2. **AV node** → ~120 ms delay (allows diastolic filling)
3. **Bundle of His → Bundle branches → Purkinje fibres** → coordinated ventricular activation

Disorders: AV block I–III, bundle branch block, atrial fibrillation (irregularly irregular,
absent P-waves on ECG).

## Clinical Measurement Technology

Blood pressure monitors (NIBP): Korotkoff phases for auscultatory method, oscillometry
for automated measurement. Cardiac ultrasound (echocardiography): Doppler effect for flow
measurement, 2D/3D B-mode for anatomy. Implantable cardiac pacemakers (ICD/CRT) must be
tested according to IEC 60601-2-27.
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 3. Blutdruckmessung (NIBP)
    # ──────────────────────────────────────────────────────────────
    "blutdruck_messung": [
        {
            "title_de": "Blutdruckmessung (NIBP)",
            "title_en": "Non-Invasive Blood Pressure Measurement (NIBP)",
            "body_de": """\
## Grundprinzip und historische Entwicklung

Blutdruck wird in mmHg angegeben (1 mmHg = 133,3 Pa). Riva-Rocci (1896) führte die
Sphygmomanometrie mit Oberarmmanschette ein; Korotkoff (1905) beschrieb den auskultatorischen
Nachweis durch Gefäßgeräusche.

## Auskultatorische Methode

Eine Manschette wird auf ~30 mmHg über den systolischen Druckwert aufgepumpt, danach
langsam (~2–3 mmHg/s) abgelassen. Mit einem Stethoskop über der A. brachialis hört man:

| Phase | Geräusch | Bedeutung |
|-------|----------|-----------|
| I | Erstes klares Klopfgeräusch | Systolischer Druck |
| II | Geräusche weicher, rauschend | Turbulenz nimmt ab |
| III | Geräusch wird lauter/klarer | – |
| IV | Geräusch abrupt dumpfer | Diastolischer Druck (alternativ) |
| V | Geräusch verschwindet | Diastolischer Druck (Standard) |

## Oszillometrische Methode (automatisch)

Automatische Geräte messen Druckoszillationen in der Manschette, die durch Arterienpulsation
entstehen. Die maximale Oszillationsamplitude korreliert mit dem **mittleren arteriellen Druck**
(MAP). Systolischer und diastolischer Druck werden über gerätespezifische Algorithmen
(Hersteller-Propietär) interpoliert.

$$MAP \\approx DBP + \\frac{1}{3}(SBP - DBP)$$

## Klinische Anforderungen nach IEC 80601-2-30

- Messabweichung: ≤ ±5 mmHg mittlerer Fehler, ≤ 8 mmHg Standardabweichung
- Validierungsprotokoll: AAMI SP10, ESH-IP, BHS-Protokoll
- Manschettengröße: Breite 40 % des Armumfangs, Länge 80–100 %

## Invasive Referenzmessung (Gold-Standard)

Über einen arteriellen Katheter (meist A. radialis) wird der Druck direkt mit einem
piezoelektrischen Drucksensor gemessen. Die Systemantwort (Drucksensor + Schlauch) muss
ausreichend gedämpft und frequenzkompensiert sein (resonanzfreier Bereich > 25 Hz).
""",
            "body_en": """\
## Operating Principle

Blood pressure is expressed in mmHg (1 mmHg = 133.3 Pa). The oscillometric method used in
automated NIBP devices measures pressure oscillations within the cuff caused by arterial
pulsations. The maximum oscillation amplitude correlates with the **mean arterial pressure
(MAP)**:

$$MAP \\approx DBP + \\frac{1}{3}(SBP - DBP)$$

Systolic and diastolic pressures are derived from proprietary algorithms applied to the
oscillation envelope.

## Auscultatory Method

The cuff is inflated to ~30 mmHg above systolic pressure, then slowly deflated
(~2–3 mmHg/s). Korotkoff sounds heard over the brachial artery mark:
- **Phase I** (first clear knock) → systolic pressure
- **Phase V** (sounds disappear) → diastolic pressure

## IEC 80601-2-30 Clinical Requirements

- Maximum mean error: ≤ ±5 mmHg; standard deviation: ≤ 8 mmHg
- Validation protocols: AAMI SP10, ESH-IP, BHS
- Cuff dimensions: width 40 % of arm circumference, length 80–100 %

## Invasive Reference (Gold Standard)

An arterial catheter (usually radial artery) with a piezoelectric pressure transducer
provides continuous, beat-by-beat measurement. The tubing-transducer system must have
a resonance-free bandwidth > 25 Hz and adequate damping to avoid overshoot artefacts.
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 4. EKG Grundlagen
    # ──────────────────────────────────────────────────────────────
    "ekg_grundlagen": [
        {
            "title_de": "EKG Grundlagen",
            "title_en": "ECG Fundamentals",
            "body_de": """\
## Das Elektrokardiogramm (EKG)

Das EKG (Elektrokardiogramm) zeichnet die summarischen elektrischen Aktivitäten aller
Herzmuskelzellen auf. Standardmäßig werden 12 Ableitungen verwendet (Einthoven I–III,
Goldberger aVR/aVL/aVF, Wilson V1–V6).

## Signalcharakteristik und Wellenformen

| Segment/Welle | Bedeutung | Normwert |
|--------------|-----------|----------|
| P-Welle | Vorhoferregung | < 120 ms, < 0,25 mV |
| PQ-Intervall | AV-Überleitung | 120–200 ms |
| QRS-Komplex | Kammererregung | < 120 ms |
| ST-Strecke | Plateau der Kammerdepolarisation | Isoelektrisch ±1 mm |
| T-Welle | Kammerrepolarisation | ≥ 0,1 mV |
| QT-Intervall | Gesamterregung Ventrikel | ≤ 440 ms (♂), ≤ 460 ms (♀) |

Das **korrigierte QT-Intervall** nach Bazett:

$$QT_c = \\frac{QT}{\\sqrt{RR}}$$

## Elektroden und Verstärkertechnik

EKG-Elektroden (AgCl) erzeugen eine elektrochemische Grenz­fläche zwischen Elektrolyt-Gel
und der Ag/AgCl-Elektrodenfläche. Das differentielle Eingangsverstärker­prinzip mit hoher
CMRR (> 80 dB) unterdrückt Netzstörungen (50/60 Hz). Typische EKG-Signalparameter:

- Amplitude: 0,1–5 mV
- Frequenzband: 0,05–150 Hz (-3 dB)
- Eingangsimpedanz: > 10 MΩ

## Klinische Diagnose-Anwendungen

- Ischämie / Myokardinfarkt: ST-Elevation (STEMI) oder -Depression
- Rhythmusstörungen: Vorhofflimmern, ventrikuläre Tachykardie, Kammerflimmern
- Hypertrophie: hohe R-Zacken in V5/V6 (LVH), S in V1 + R in V5 > 3,5 mV (Sokolow)
- Long-QT-Syndrom: erhöhtes Torsade-de-Pointes-Risiko

## Geräteanforderungen nach IEC 60601-2-27

Mindest-Frequenzgang: 0,67–40 Hz (Durchgangsanforderung Klasse I) oder 0,05–150 Hz
(Hochleistungsklasse). Schutzklasse: CF (direkt an Herz) oder BF (nicht direkt).
""",
            "body_en": """\
## The Electrocardiogram (ECG)

The ECG records the summated electrical activity of all cardiac muscle cells.
The standard 12-lead system uses Einthoven leads I–III, augmented leads aVR/aVL/aVF, and
precordial leads V1–V6.

## Signal Characteristics and Waveforms

| Segment/Wave | Meaning | Normal Value |
|-------------|---------|--------------|
| P-wave | Atrial depolarisation | < 120 ms, < 0.25 mV |
| PR interval | AV conduction time | 120–200 ms |
| QRS complex | Ventricular depolarisation | < 120 ms |
| ST segment | Ventricular plateau | Isoelectric ±1 mm |
| T-wave | Ventricular repolarisation | ≥ 0.1 mV |
| QT interval | Total ventricular excitation | ≤ 440 ms (♂), ≤ 460 ms (♀) |

Bazett's corrected QT interval:

$$QT_c = \\frac{QT}{\\sqrt{RR}}$$

## Amplifier Technology

ECG electrodes (Ag/AgCl) create an electrochemical interface. A differential input amplifier
with high CMRR (> 80 dB) suppresses mains interference (50/60 Hz). Typical ECG signal
parameters: amplitude 0.1–5 mV, bandwidth 0.05–150 Hz, input impedance > 10 MΩ.

## IEC 60601-2-27 Requirements

Minimum frequency response: 0.67–40 Hz (Class I) or 0.05–150 Hz (high-quality class).
Patient connection type: CF (direct cardiac) or BF (non-cardiac contact).
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 5. Pulsoximetrie
    # ──────────────────────────────────────────────────────────────
    "pulsoximetrie": [
        {
            "title_de": "Pulsoximetrie",
            "title_en": "Pulse Oximetry",
            "body_de": """\
## Messprinzip

Die Pulsoxymetrie misst die funktionelle Sauerstoffsättigung (SpO₂) des arteriellen Blutes
nicht-invasiv. Sie nutzt das Lambert-Beer'sche Gesetz:

$$I = I_0 \\cdot e^{-\\varepsilon \\cdot c \\cdot d}$$

Oxygeniertes Hämoglobin (HbO₂) und desoxigeniertes Hämoglobin (Hb) haben unterschiedliche
Extinktionskoeffizienten bei zwei Wellenlängen:

| Wellenlänge | HbO₂ | Hb |
|-------------|------|----|
| 660 nm (rot) | niedrig | hoch |
| 940 nm (infrarot) | hoch | niedrig |

Der **R-Ratio** (ratio of ratios) wird berechnet:

$$R = \\frac{AC_{660}/DC_{660}}{AC_{940}/DC_{940}}$$

Aus R wird SpO₂ über eine empirisch kalibrierte Lookup-Table ermittelt (Kalibrierung
an Probandenstudien mit arterieller BGA als Referenz).

## Signalverarbeitung

Das Pulsoxymetersignal enthält:
- **DC-Anteil**: venöses Blut, Gewebe, Haut (konstant)
- **AC-Anteil**: pulsatiles arterielles Blut (synchron mit Herzschlag)

Nur der AC-Anteil ist diagnostisch relevant. Signalqualität-Algorithmen erkennen
Bewegungsartefakte (adaptive Filterung, Wavelet-Dekomposition).

## Limitierungen

- Unzuverlässig bei SpO₂ < 70 % (extrapoliert)
- Carboxyhämoglobin (CO-Vergiftung) und MetHb werden als HbO₂ fehlinterpretiert
- Schlechte Perfusion (Schock, periphere Durchblutungsstörung), Nagellack
- Klinisch wichtig: SpO₂ ≠ PaO₂ (Sättigungskurve nach rechts/links verschoben)

## Normwerte und klinische Alarmschwellen

SpO₂ normal: 95–100 %. Alarm: SpO₂ < 90–94 % (klinisch festgelegt). Laut IEC 60601-2-61
muss die Genauigkeit ±3 % (RMSD) bei 70–100 % SpO₂ betragen.
""",
            "body_en": """\
## Measurement Principle

Pulse oximetry non-invasively measures functional arterial oxygen saturation (SpO₂) using
the Beer–Lambert law. Oxygenated (HbO₂) and deoxygenated (Hb) haemoglobin have different
extinction coefficients at two wavelengths:

| Wavelength | HbO₂ | Hb |
|------------|------|----|
| 660 nm (red) | low | high |
| 940 nm (infrared) | high | low |

The **ratio of ratios (R)**:

$$R = \\frac{AC_{660}/DC_{660}}{AC_{940}/DC_{940}}$$

SpO₂ is derived from R via an empirically calibrated look-up table (validated against
arterial blood gas as reference in volunteer studies).

## Signal Components

- **DC component**: venous blood, tissue, skin (constant over time)
- **AC component**: pulsatile arterial blood (heart-synchronous)

Only the AC component carries diagnostic information. Motion artefact rejection uses
adaptive filtering and wavelet decomposition.

## Limitations and IEC 60601-2-61 Requirements

COHb and MetHb are misread as HbO₂. Accuracy per IEC 60601-2-61: ±3 % RMSD for
70–100 % SpO₂. Clinical alert threshold typically set at SpO₂ < 90–94 %.
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 6. Ohmsches Gesetz in der Medizintechnik
    # ──────────────────────────────────────────────────────────────
    "ohmsches_gesetz": [
        {
            "title_de": "Ohmsches Gesetz in der Medizintechnik",
            "title_en": "Ohm's Law in Medical Technology",
            "body_de": """\
## Grundgesetz der Elektrizität

Das Ohmsche Gesetz beschreibt die lineare Beziehung zwischen Spannung U, Strom I und
Widerstand R:

$$U = R \\cdot I \\quad \\Leftrightarrow \\quad R = \\frac{U}{I} \\quad \\Leftrightarrow \\quad I = \\frac{U}{R}$$

Einheiten: U in Volt (V), I in Ampere (A), R in Ohm (Ω).

## Gewebsimpedanz und Bioimpedanz

Biologisches Gewebe verhält sich nicht wie ein rein ohmscher Widerstand — es besitzt
kapazitive Anteile (Zellmembranen als Dielektrikum). Die **Gewebsimpedanz** Z ist
frequenzabhängig:

$$Z(\\omega) = R + \\frac{1}{j\\omega C} \\quad (Reihenschaltung)$$

Bei der **Bioimpedanzanalyse (BIA)** werden Wechselströme mehrerer Frequenzen (1 kHz –
1 MHz) angelegt. Aus den Widerstandskomponenten (R, Xc) berechnet man Körperzusammen­setzung
(Fettmasse, Muskelmasse, Hydratationsstatus).

## Elektrische Sicherheit — Körperstrom und Fibrillationsgefahr

Der Körperwiderstand (Haut–Haut, trocken) beträgt 1 kΩ–100 kΩ, feucht nur 1 kΩ.
Gefährliche Ströme:

| Strom (50 Hz) | Wirkung |
|--------------|---------|
| < 1 mA | Keine Wahrnehmung |
| 1–10 mA | Kribbeln, Loslassschwelle ~10 mA |
| 10–100 mA | Muskelkrämpfe, Atemstillstand |
| > 100 mA | Kammerflimmern möglich |
| 50 µA (direkt am Herz) | Mikroschock — Kammerflimmern |

IEC 60601-1 legt daher Grenzwerte für Ableitströme fest:
- Gehäuseableitstrom: ≤ 100 µA (Normal) / 500 µA (Einzelfehler)
- Patientenableitstrom: ≤ 10 µA (CF-Typ, direkte Herzanwendung)

## Kirchhoffsche Gesetze in der Schaltungsanalyse

**KVL** (Maschenregel): Die Summe der Spannungen in einer geschlossenen Masche ist 0.  
**KCL** (Knotenregel): Die Summe der Ströme in einem Knoten ist 0.
Diese Gesetze bilden die Grundlage aller Schaltungsanalysen in medizintechnischen Geräten.
""",
            "body_en": """\
## The Fundamental Law of Electricity

Ohm's law describes the linear relationship between voltage U, current I and resistance R:

$$U = R \\cdot I \\quad \\Leftrightarrow \\quad R = \\frac{U}{I}$$

## Tissue Impedance and Bioimpedance

Biological tissue is not purely resistive — cell membranes act as capacitors. Tissue
impedance Z is frequency-dependent:

$$Z(\\omega) = R + \\frac{1}{j\\omega C}$$

**Bioimpedance analysis (BIA)** applies alternating currents at multiple frequencies
(1 kHz–1 MHz) to determine body composition (fat mass, muscle mass, hydration).

## Electrical Safety — Body Current and Fibrillation Risk

Skin-to-skin resistance (dry): 1 kΩ–100 kΩ; wet: ~1 kΩ.  
IEC 60601-1 patient leakage current limits:
- CF type (direct cardiac application): ≤ 10 µA
- BF type: ≤ 100 µA
- Normal condition enclosure leakage: ≤ 100 µA

Currents > 100 mA at 50/60 Hz or > 50 µA (microshock, direct cardiac) can cause
ventricular fibrillation.
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 7. Kondensatoren und Spulen
    # ──────────────────────────────────────────────────────────────
    "kondensatoren": [
        {
            "title_de": "Kondensatoren und Spulen in der Medizintechnik",
            "title_en": "Capacitors and Inductors in Medical Technology",
            "body_de": """\
## Kondensator (Kapazität)

Ein Kondensator speichert elektrische Energie im elektrischen Feld zwischen zwei Leitern.
Kapazität C in Farad (F):

$$C = \\varepsilon_0 \\varepsilon_r \\frac{A}{d}$$

Strom–Spannungs-Relation: $I = C \\frac{dU}{dt}$

Impedanz im Frequenzbereich: $Z_C = \\frac{1}{j\\omega C}$ → bei hohen Frequenzen niedrig.

**Anwendungen in der Medizintechnik:**
- Hochpass-Filter (DC-Blockierung) in EKG-Eingangsstufe
- Stützkondensatoren in Netzteil-Schaltreglern
- Elektrolyt-Kapazitäten in Defibrillator-Energiespeichern (z. B. 32 µF, 5 kV → 400 J)

## Spule (Induktivität)

Eine Spule speichert Energie im magnetischen Feld.
Induktivität L in Henry (H): $U = L \\frac{dI}{dt}$

Impedanz: $Z_L = j\\omega L$ → bei hohen Frequenzen hochohmig.

**Anwendungen:**
- Tiefpass-Filter (EMV-Filter) in Netzteilen
- Wireless Charging (induktive Energieübertragung) in implantierbaren Geräten
- HF-Spulen in MRT-Systemen (Empfangs- und Sendespulen)

## Schwingkreis und Resonanz

Ein LC-Schwingkreis hat eine Resonanzfrequenz:

$$f_0 = \\frac{1}{2\\pi\\sqrt{LC}}$$

Bei Resonanz ist die Impedanz rein reell (paralleler Schwingkreis: maximal, seriell:
minimal). MRT-HF-Spulen sind auf die Larmorfrequenz ($f_L = \\gamma B_0 / 2\\pi$)
abgestimmt.

## Praktisches Beispiel — Defibrillator

Ein Defibrillator lädt einen Kondensator C = 150 µF auf U = 2000 V:

$$W = \\frac{1}{2} C U^2 = \\frac{1}{2} \\cdot 150 \\times 10^{-6} \\cdot 4 \\times 10^6 = 300\\,J$$

Die Entladung über eine Induktivität erzeugt eine gedämpfte Sinusschwingung (biphasischer
Schock: besserer Wirkungsgrad, weniger Myokardschaden).
""",
            "body_en": """\
## Capacitor

A capacitor stores energy in the electric field between two conductors:

$$C = \\varepsilon_0 \\varepsilon_r \\frac{A}{d}, \\quad I = C \\frac{dU}{dt}, \\quad Z_C = \\frac{1}{j\\omega C}$$

**Medical applications:** High-pass filter (DC blocking) in ECG front-end; electrolytic
capacitors in defibrillator energy storage (e.g. 32 µF, 5 kV → 400 J).

## Inductor

An inductor stores energy in the magnetic field:

$$U = L \\frac{dI}{dt}, \\quad Z_L = j\\omega L$$

**Medical applications:** EMC filters in power supplies; inductive wireless charging for
implantable devices; RF coils in MRI systems.

## LC Resonance

$$f_0 = \\frac{1}{2\\pi\\sqrt{LC}}$$

MRI RF coils are tuned to the Larmor frequency ($f_L = \\gamma B_0 / 2\\pi$).

## Defibrillator Example

Capacitor C = 150 µF charged to U = 2000 V stores:

$$W = \\frac{1}{2} C U^2 = 300\\,J$$

Discharge through an inductor creates a damped sinusoidal waveform (biphasic shock).
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 8. Verstärkerschaltungen für Biosignale
    # ──────────────────────────────────────────────────────────────
    "verstaerker": [
        {
            "title_de": "Verstärkerschaltungen für Biosignale",
            "title_en": "Amplifier Circuits for Biosignals",
            "body_de": """\
## Operationsverstärker (OPV)

Der ideale Operationsverstärker hat:
- Unendliche Leerlaufverstärkung: $A_{OL} \\rightarrow \\infty$
- Unendliche Eingangsimpedanz
- Null-Ausgangsimpedanz
- Kein Offset, kein Rauschen

Reale Kennwerte typischer Instrumentenverstärker (z. B. AD8221):
- CMRR: 80–100 dB
- Eingangsimpedanz: > 100 GΩ
- Eingangsstromrauschen: 7 fA/√Hz

## Instrumentenverstärker (INA)

Der INA besteht aus drei OPVs und liefert:

$$U_{out} = \\left(1 + \\frac{2R}{R_G}\\right)(U^+ - U^-)$$

Durch Wahl von $R_G$ lässt sich die Verstärkung einstellen. Hohe CMRR ist entscheidend
für EKG- und EEG-Messungen, da Störsignale (Netzbrummen, statische Aufladung) als
Gleichtaktsignal auftreten.

## Grundschaltungen

| Schaltung | Formel | Anwendung |
|-----------|--------|-----------|
| Invertierender Verstärker | $V = -R_2/R_1$ | Signalumkehr + Verstärkung |
| Nichtinvertierender Verstärker | $V = 1 + R_2/R_1$ | Impedanzanpassung |
| Spannungsfolger (Buffer) | $V = 1$ | Impedanzwandlung |
| Differenzverstärker | $V = R_2/R_1$ | Differenzmessung |
| Integrator | $U_{out} = -\\frac{1}{RC}\\int U_{in}\\,dt$ | Tiefpass, Ladungsmessung |

## Rauschen und Signal-Rausch-Abstand

Das thermische Widerstandsrauschen (Johnson-Nyquist):

$$U_{n,rms} = \\sqrt{4kTRB}$$

mit k = 1,38 × 10⁻²³ J/K, T in Kelvin, B = Bandbreite.

Für R = 10 kΩ, T = 310 K, B = 1 kHz: $U_{n,rms} \\approx 13\\,\\text{nV}/\\sqrt{\\text{Hz}}$

**SNR** = 20 log₁₀(Signal / Rauschen). EEG-Signale (< 100 µV) erfordern extrem rauscharme
Eingangsstufen mit SNR > 60 dB.

## Schutzschaltungen für Patientensicherheit

- Eingangsbegrenzung (TVS-Dioden) gegen Defibrillatorimpulse (> 5 kV, 360 J)
- Optokoppler oder kapazitive Isolation für galvanische Trennung
- Hochspannungs-Isolierbarrier (nach IEC 60601-1): ≥ 4 kV Prüfspannung
""",
            "body_en": """\
## Operational Amplifier (Op-Amp)

An ideal op-amp has infinite open-loop gain, infinite input impedance, and zero output
impedance. Real instrumentation amplifiers (e.g. AD8221) achieve: CMRR 80–100 dB,
input impedance > 100 GΩ, current noise 7 fA/√Hz.

## Instrumentation Amplifier (INA)

Three-op-amp topology with gain set by external resistor $R_G$:

$$U_{out} = \\left(1 + \\frac{2R}{R_G}\\right)(U^+ - U^-)$$

High CMRR suppresses common-mode interference (mains hum, electrostatic noise) critical
for ECG and EEG acquisition.

## Noise and SNR

Thermal (Johnson–Nyquist) noise:

$$U_{n,rms} = \\sqrt{4kTRB}$$

EEG signals (< 100 µV) require input stages with SNR > 60 dB.

## Patient Protection Circuits

- TVS diode clamping for defibrillator pulse protection (> 5 kV)
- Capacitive or optical isolation for galvanic separation
- Isolation barrier: ≥ 4 kV test voltage per IEC 60601-1
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 9. Analog-Digital-Wandlung
    # ──────────────────────────────────────────────────────────────
    "analog_digital": [
        {
            "title_de": "Analog-Digital-Wandlung (ADC)",
            "title_en": "Analog-to-Digital Conversion (ADC)",
            "body_de": """\
## Grundprinzip der Quantisierung

Ein Analog-Digital-Wandler (ADC) konvertiert ein kontinuierliches analoges Signal in eine
diskrete digitale Darstellung. Zwei Prozesse sind wesentlich:

1. **Abtastung** (Sampling): Das analoge Signal wird zu diskreten Zeitpunkten gemessen.
   Das Nyquist-Shannon-Abtasttheorem fordert:

   $$f_s \\geq 2 \\cdot f_{max}$$

   Verletzung → Aliasing (Frequenzfaltung).

2. **Quantisierung**: Die Amplitude wird auf $2^N$ Stufen gerundet.
   Quantisierungsrauschen: $e_q \\leq \\frac{LSB}{2} = \\frac{U_{ref}}{2^{N+1}}$

## ADC-Kenngrössen

| Parameter | Bedeutung |
|-----------|-----------|
| Auflösung N | Anzahl Bits, typisch 8–24 Bit |
| SNR_{ADC} | ≈ 6,02N + 1,76 dB (ideal) |
| ENOB | Effective Number of Bits |
| INL / DNL | Integral/Differentielle Nichtlinearität |
| Abtastrate f_s | Samples/Sekunde |

Für ein 12-Bit-ADC ist der ideale SNR = 6,02 × 12 + 1,76 = **74 dB**.

## ADC-Typen in der Medizintechnik

| Typ | Auflösung | Geschwindigkeit | Anwendung |
|----|---------|----------------|-----------|
| Sigma-Delta (Σ-Δ) | 16–24 Bit | Hz–kHz | EEG, SpO₂, BIA |
| SAR (Successive Approximation) | 12–18 Bit | kHz–MSPS | EKG, Ultraschall |
| Flash | 6–12 Bit | > 100 MSPS | CT/MRT-Empfänger |

## Anti-Aliasing-Filter

Vor dem ADC ist ein analoges Tiefpassfilter (Anti-Aliasing-Filter) notwendig.
Typisches Design: Butterworth oder Bessel, Grenzfrequenz $f_c = f_s / 2$.
Für EKG (f_s = 1 kHz): $f_c$ = 500 Hz → mindestens 20 dB/Dekade Absenkung.

## Beispiel: EEG-Digitalisierung

Bandbreite EEG: DC – 100 Hz. Gewählte f_s = 256 Hz (ausreichend nach Nyquist).
Benötigte Auflösung: EEG < 100 µV, Störpegel ~1 µV → SNR-Bedarf ~40 dB → 7 Bit
theoretisch, in der Praxis 24-Bit Σ-Δ-ADC für ausreichende Reserve (ENOB ~16 Bit).
""",
            "body_en": """\
## Sampling and Quantisation

An ADC converts a continuous analogue signal to a discrete digital representation via:

1. **Sampling**: Nyquist–Shannon theorem requires $f_s \\geq 2 f_{max}$; violation causes aliasing.
2. **Quantisation**: Amplitude rounded to $2^N$ levels; quantisation noise $\\leq LSB/2$.

Ideal ADC SNR: $SNR = 6.02N + 1.76\\,dB$

## ADC Types in Medical Devices

| Type | Resolution | Speed | Application |
|------|-----------|-------|-------------|
| Sigma-Delta | 16–24 bit | Hz–kHz | EEG, SpO₂, BIA |
| SAR | 12–18 bit | kHz–MSPS | ECG, ultrasound |
| Flash | 6–12 bit | > 100 MSPS | CT/MRI receivers |

## Anti-Aliasing Filter

An analogue low-pass filter (Butterworth or Bessel, $f_c = f_s/2$) must precede the ADC
to prevent aliasing. For an ECG sampler at 1 kHz: $f_c = 500$ Hz.

## EEG Example

EEG bandwidth: DC–100 Hz. Sampling rate: 256 Hz (Nyquist-compliant).
Required SNR ~40 dB → 7 bits theoretical minimum → 24-bit Σ-Δ ADC used in practice
for adequate headroom (ENOB ~16 bits).
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 10. Signalfilterung und DSP
    # ──────────────────────────────────────────────────────────────
    "signalfilterung": [
        {
            "title_de": "Signalfilterung und Digitale Signalverarbeitung (DSP)",
            "title_en": "Signal Filtering and Digital Signal Processing (DSP)",
            "body_de": """\
## Filter-Grundtypen

| Typ | Durchlassbereich | Anwendung (Medizintechnik) |
|----|-----------------|--------------------------|
| Tiefpass (LP) | f < f_c | Glättung, Anti-Aliasing |
| Hochpass (HP) | f > f_c | DC-Offset-Entfernung (EKG) |
| Bandpass (BP) | f₁ < f < f₂ | EKG R-Zacken-Detektion |
| Bandsperre (Notch) | f ≈ 50 Hz | Netzbrummen-Unterdrückung |

## IIR vs. FIR Filter

**FIR** (Finite Impulse Response): Linear-phase möglich, immer stabil, hohe Filterordnung.

$$y[n] = \\sum_{k=0}^{N} b_k \\cdot x[n-k]$$

**IIR** (Infinite Impulse Response): Niedriger Rechenaufwand, aber Phasendrehung, Stabilitätsproblem.

$$y[n] = \\sum_{k=0}^{N} b_k x[n-k] - \\sum_{k=1}^{M} a_k y[n-k]$$

Für EKG-Anwendungen werden oft **linearphasige FIR-Filter** bevorzugt, um die
Signalform (klinische Diagnose) nicht zu verzerren.

## Fourier-Transformation und Spektralanalyse

Die **diskrete Fourier-Transformation (DFT)** und ihre schnelle Implementierung (FFT,
Cooley-Tukey) analysieren das Frequenzspektrum eines Signals:

$$X[k] = \\sum_{n=0}^{N-1} x[n] \\cdot e^{-j2\\pi kn/N}$$

Anwendungen: HRV-Analyse (LF/HF-Power-Spektrum), EEG-Frequenzbänder (Delta, Theta,
Alpha, Beta, Gamma), Ultraschall-Doppler-Spektrum.

## Notch-Filter für 50-Hz-Störung

Bilineare z-Transformation eines kontinuierlichen Notch-Filters. Güte Q = f₀/BW.
Für f₀ = 50 Hz, BW = 2 Hz: Q = 25. Achtung: Standard-EKG nach IEC 60601-2-27
schreibt vor, dass ein 50-Hz-Filter als Abschaltbarer Modus implementiert sein muss
(Diagnose-EKG benötigt 50-Hz-Komponente für ST-Analyse).

## Pan-Tompkins-Algorithmus (QRS-Detektion)

Kanonischer Algorithmus zur R-Zacken-Detektion im EKG:
1. Bandpass (5–15 Hz)
2. Differentiation
3. Quadrierung
4. Moving Window Averaging
5. Schwellwert-Entscheidung (adaptiv)

Liefert Herzrate und RR-Intervall-Sequenz für HRV-Analyse.
""",
            "body_en": """\
## Filter Types

| Type | Pass-band | Medical Application |
|-----|-----------|---------------------|
| Low-pass | f < f_c | Smoothing, anti-aliasing |
| High-pass | f > f_c | DC offset removal (ECG) |
| Band-pass | f₁ < f < f₂ | QRS detection |
| Notch | f ≈ 50/60 Hz | Mains interference rejection |

## FIR vs. IIR

**FIR**: Linear phase possible (preserves waveform shape), always stable, higher order needed.  
**IIR**: Lower computational cost but introduces phase distortion.

$$y[n] = \\sum_{k=0}^{N} b_k x[n-k] - \\sum_{k=1}^{M} a_k y[n-k]$$

Linear-phase FIR filters are preferred for ECG applications to avoid clinical waveform
distortion.

## FFT and Spectral Analysis

$$X[k] = \\sum_{n=0}^{N-1} x[n] \\cdot e^{-j2\\pi kn/N}$$

Applications: HRV LF/HF power spectrum, EEG frequency bands, Doppler ultrasound spectrum.

## Pan–Tompkins QRS Detection

1. Band-pass (5–15 Hz) → 2. Differentiation → 3. Squaring →
4. Moving window averaging → 5. Adaptive thresholding

Provides heart rate and RR interval sequence for HRV analysis.
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 11. MDR 2017/745 Grundlagen
    # ──────────────────────────────────────────────────────────────
    "mdr_grundlagen": [
        {
            "title_de": "MDR 2017/745 — Grundlagen der EU-Medizinprodukteverordnung",
            "title_en": "MDR 2017/745 — EU Medical Devices Regulation Fundamentals",
            "body_de": """\
## Überblick und Geltungsbereich

Die **EU-Medizinprodukteverordnung (MDR) 2017/745** gilt seit 26. Mai 2021 (vollständig ab
26. Mai 2021, verlängerte Übergangfristen bis 2024/2027 für bestimmte Klassen). Sie
ersetzt die Richtlinien MDD 93/42/EWG und AIMDD 90/385/EWG.

Geltungsbereich: Alle Medizinprodukte, die auf dem EU-Markt in Verkehr gebracht werden.
Definition Medizinprodukt (Art. 2): Instrument, Gerät, Software etc., zur Diagnose,
Prophylaxe, Therapie, Überwachung oder Linderung von Krankheiten beim Menschen.

**Software als Medizinprodukt (SaMD)**: Nach MDR kann Software selbst als Medizinprodukt
eingestuft werden (Art. 2 Nr. 1), wenn sie eigenständig diagnostische oder therapeutische
Zwecke erfüllt.

## Klassifizierung (Anhang VIII)

Die Risikoklassifizierung richtet sich nach Invasivitätsgrad, Kontaktdauer und
Anwendungsbereich:

| Klasse | Risiko | Beispiele |
|--------|--------|-----------|
| I | Gering | Rollstühle, Verbände |
| IIa | Mäßig | Hörgeräte, nicht-invasive Blutdruckmessgeräte |
| IIb | Erhöht | Beatmungsgeräte, aktive Implantate-Zubehör |
| III | Hoch | Herzklappen, Koronarstents, aktive Implantate |

## Grundlegende Sicherheits- und Leistungsanforderungen (Anhang I)

Hersteller müssen nachweisen, dass:
- Risiken minimiert sind (Risiko-Nutzen-Abwägung)
- Nichtklinische und klinische Bewertung durchgeführt wurde
- Gebrauchsanweisung (IFU), Kennzeichnung vorhanden sind
- Post-Market Surveillance (PMS) eingerichtet ist

## Technische Dokumentation und QMS

Art. 10 MDR: Hersteller benötigen ein **Qualitätsmanagementsystem** (mind. ISO 13485-konform).
Technische Dokumentation muss enthalten:
- Beschreibung und Spezifikation (inkl. Varianten)
- Angaben zu Design und Herstellung
- Grundlegende Sicherheits- und Leistungsanforderungen
- Nutzen-Risiko-Analyse (ISO 14971)
- Klinische Bewertung (MEDDEV 2.7/1 Rev. 4)
- Post-Market Clinical Follow-up (PMCF)

## Notifizierte Stellen und CE-Kennzeichnung

Klasse IIa–III: Konformitätsbewertung durch **Notifizierte Stelle** (NB) erforderlich.
CE-Kennzeichnung + NB-Nummer auf dem Produkt nach erfolgreicher Bewertung.
EU-Datenbank: **EUDAMED** (European Database on Medical Devices) für Transparenz.
""",
            "body_en": """\
## Scope and Definition

**EU MDR 2017/745** has applied since 26 May 2021, replacing MDD 93/42/EEC. It covers all
medical devices placed on the EU market. A medical device (Art. 2) is any instrument,
apparatus, software, etc. intended for diagnosis, prevention, monitoring or treatment of
disease in humans.

Software as a Medical Device (SaMD): Software that independently fulfils diagnostic or
therapeutic purposes qualifies as a medical device under Art. 2(1).

## Classification (Annex VIII)

| Class | Risk | Examples |
|-------|------|---------|
| I | Low | Wheelchairs, bandages |
| IIa | Moderate | Hearing aids, NIBP monitors |
| IIb | Elevated | Ventilators |
| III | High | Heart valves, coronary stents |

## Essential Safety and Performance Requirements (Annex I)

Manufacturers must demonstrate: risk minimisation, clinical evaluation, adequate IFU and
labelling, and an established Post-Market Surveillance (PMS) system.

## QMS and Technical Documentation

Art. 10 MDR requires a Quality Management System (ISO 13485 compliant). Technical
documentation must include device description, design/manufacturing information, risk/benefit
analysis (ISO 14971), clinical evaluation (MEDDEV 2.7/1 Rev. 4), and PMCF plan.

## Notified Bodies and CE Marking

Classes IIa–III require conformity assessment by a **Notified Body (NB)**.
CE marking + NB number affixed to the product. EUDAMED database ensures EU-wide transparency.
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 12. Risikoanalyse nach ISO 14971
    # ──────────────────────────────────────────────────────────────
    "risikoanalyse_iso14971": [
        {
            "title_de": "Risikoanalyse nach ISO 14971",
            "title_en": "Risk Analysis according to ISO 14971",
            "body_de": """\
## Scope und Grundkonzept

**ISO 14971:2019** ist die internationale Norm für das Risikomanagement von Medizinprodukten.
Sie definiert einen systematischen Prozess zur Identifikation von Gefährdungen, Schätzung
und Bewertung von Risiken sowie zur Kontrolle und Überwachung dieser Risiken.

**Grundbegriffe:**

| Begriff | Definition |
|---------|-----------|
| Gefährdung (Hazard) | Mögliche Schadensquelle |
| Gefährdungssituation | Umstände, die Exposition gegenüber Gefährdung verursachen |
| Schaden (Harm) | Physische Verletzung oder Gesundheitsschaden |
| Wahrscheinlichkeit P | P(Schaden eintreten) = P(Gefährdungssituation) × P(Schaden|Situ.) |
| Schwere S | Ausmaß des Schadens (z. B. 1–5 Skala) |
| Risiko R | R = P × S |

## Risikomanagementprozess (5 Phasen)

```
1. Risikoanalyse
   ├── Zweckbestimmung
   ├── Identifikation bekannter/vorhersehbarer Gefährdungen
   └── Risikoschätzung (P × S)

2. Risikobewertung
   └── Vergleich mit Risikoakzeptanzkriterien (ALARP)

3. Risikokontrolle
   ├── a) Sicherheit durch Design
   ├── b) Schutzmaßnahmen
   └── c) Sicherheitsinformationen (IFU, Warnhinweise)

4. Verbleibende Risiken + Gesamtrisiko-Nutzen-Abwägung

5. Post-Market Surveillance (PMS)
```

## FMEA und FTA als Werkzeuge

**FMEA** (Failure Mode and Effects Analysis): Bottomup-Analyse.
Für jede Komponente werden Ausfallarten, Auswirkungen und Entdeckungswahrscheinlichkeit
bewertet. RPN = Bedeutung × Auftreten × Entdeckung.

**FTA** (Fault Tree Analysis): Topdown-Analyse. Vom unerwünschten Ereignis (Top-Event)
werden logisch Ursachenketten (AND/OR-Gates) bis zu Basisereignissen abgeleitet.

## Normative Verweiskette

ISO 14971 → EN ISO 14971 (harmonisiert unter MDR) → ISO/TR 24971 (Guidance) →
MEDDEV 2.7/1 Rev.4 (klinische Bewertung, Nutzen-Risiko).

Wichtig: ISO 14971 gilt für den **gesamten Produktlebenszyklus** (Design → Herstellung →
Verwendung → Entsorgung), nicht nur für die Designphase.
""",
            "body_en": """\
## Scope and Core Concepts

**ISO 14971:2019** provides the framework for medical device risk management:
systematic identification of hazards, risk estimation and evaluation, and risk control.

**Key Terms:**

| Term | Definition |
|------|-----------|
| Hazard | Potential source of harm |
| Hazardous situation | Circumstances exposing individuals to a hazard |
| Harm | Physical injury or damage to health |
| Risk R | R = Probability × Severity |
| ALARP | As Low As Reasonably Practicable |

## Risk Management Process

1. Risk analysis (hazard identification, risk estimation)
2. Risk evaluation (compare against acceptance criteria)
3. Risk control: (a) design safety, (b) protective measures, (c) safety information (IFU)
4. Residual risk and overall benefit-risk assessment
5. Post-market surveillance

## FMEA and FTA

**FMEA** (bottom-up): RPN = Severity × Occurrence × Detectability per failure mode.  
**FTA** (top-down): Logical AND/OR gate tree from undesired top-event to basic causes.

## Normative Chain

ISO 14971 → EN ISO 14971 (harmonised under MDR) → ISO/TR 24971 (guidance) →
MEDDEV 2.7/1 Rev.4 (clinical evidence, benefit-risk).

ISO 14971 applies across the **entire product lifecycle** (design → manufacture → use → disposal).
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 13. IEC 62304 — Software-Lebenszyklus
    # ──────────────────────────────────────────────────────────────
    "iec_62304": [
        {
            "title_de": "Software-Lebenszyklus nach IEC 62304",
            "title_en": "Software Lifecycle per IEC 62304",
            "body_de": """\
## Einordnung und Geltungsbereich

**IEC 62304:2006 + AMD1:2015** definiert Anforderungen an den Lebenszyklus von
Medizinprodukte-Software und Software, die in Medizinprodukten eingebettet ist (Firmware).
Die Norm ist unter MDR harmonisiert und gilt als State-of-the-Art für SaMD und embedded
Software.

## Software-Sicherheitsklassen (Safety Classes)

| Klasse | Gefährdung durch Software-Ausfall | Beispiele |
|--------|---------------------------------|-----------|
| A | Keine Verletzung oder Schaden | Patientenverwaltung, Archivierung |
| B | Nicht-schwerwiegende Verletzung | Dosisberechnungs-Assistent (mit manueller Überprüfung) |
| C | Tod oder schwerwiegende Verletzung | Beatmungssteuerung, Insulinpumpe, Röntgensteuerung |

## Software-Entwicklungsprozess (Kapitel 5)

```
5.1 Softwareentwicklungsplanung
5.2 Software-Anforderungsanalyse
5.3 Software-Architekturentwurf
5.4 Software-Detaildesign
5.5 Software-Unit-Implementierung und -Verifizierung
5.6 Software-Integration und -Integration-Test
5.7 Software-System-Test
5.8 Software-Freigabe
```

Für Klasse A: nur 5.1, 5.2, 5.8 verpflichtend.
Für Klasse B: vollständiger Prozess, kein verpflichtender Detaildesign.
Für Klasse C: vollständiger Prozess inkl. detaillierter Designdokumentation.

## Konfigurationsmanagement und Problemlösung

- **5.1.4** Konfigurationsmanagementplan (Versionierung, Änderungskontrolle)
- **6.** Konfigurationsmanagement (u. a. Buildprozess, Baselining)
- **9.** Problemlösungsprozess (Bug-Tracking, Wurzelursachenanalyse, Rückwirkungsprüfung)

## Verifikation und Validierung

**Verifikation** (korrekte Implementierung der Spezifikation): Unit-Tests, Code-Review,
statische Analyse (MISRA C, SonarQube).  
**Validierung** (richtiges Produkt für den Anwender): Usability-Tests (IEC 62366),
klinische Bewertung.

Formal akzeptiere Testmethoden für Klasse C: Statement Coverage ≥ 100 %, Zweig-Coverage
≥ 100 %, MC/DC-Coverage für sicherheitskritische Module.

## SOUP (Software of Unknown Provenance)

Third-Party-Bibliotheken, Open-Source-Komponenten und COTS-Software gelten als SOUP.
Anforderungen: Dokumentation, Risikoanalyse, Anomalienüberwachung (Herstellerbuglisten).
""",
            "body_en": """\
## Scope

**IEC 62304:2006+AMD1:2015** defines software lifecycle requirements for medical device
software and embedded firmware. It is harmonised under the EU MDR.

## Software Safety Classes

| Class | Hazard from software failure | Examples |
|-------|------------------------------|---------|
| A | No injury or damage | Patient administration |
| B | Non-serious injury | Dose calculation assistant |
| C | Death or serious injury | Ventilator control, insulin pump |

## Development Process (Clause 5)

Requirements analysis → Architecture design → Detailed design (class C) →
Unit implementation & verification → Integration testing → System testing → Release

Class A: only planning, requirements, and release required.
Class C: full process including detailed design documentation.

## Verification and Validation

- **Verification**: correct implementation of specifications (unit tests, code review, static analysis — MISRA C).
- **Validation**: right product for the user (usability tests per IEC 62366, clinical evaluation).

Class C coverage requirements: statement ≥ 100 %, branch ≥ 100 %, MC/DC for safety-critical modules.

## SOUP

Third-party libraries and open-source components are **SOUP** (Software of Unknown Provenance).
Requirements: documentation, risk analysis, anomaly monitoring.
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 14. Biomechanische Grundlagen
    # ──────────────────────────────────────────────────────────────
    "biomechanik_grundlagen": [
        {
            "title_de": "Biomechanische Grundlagen",
            "title_en": "Fundamentals of Biomechanics",
            "body_de": """\
## Mechanische Grundgrössen

Biomechanik beschreibt die mechanischen Eigenschaften von biologischen Geweben und
menschlichen Bewegungen. Grundgrössen:

- **Kraft** F [N]: Masse × Beschleunigung, $F = m \\cdot a$
- **Drehmoment** M [N·m]: $M = F \\times r$
- **Druck** p [Pa]: $p = F/A$, physiologisch bis 20 MPa in Knochen

## Mechanische Eigenschaften biologischer Gewebe

Knochen (kortikaler Knochen): E-Modul ~17 GPa, Bruchfestigkeit ~130 MPa (Zug).
Knorpel: E-Modul ~1–10 MPa (viskoelastisch, frequenzabhängig).
Sehnen/Bänder: E-Modul ~1,5 GPa, J-förmige Spannungs-Dehnungs-Kurve (Crimping der
Kollagenfibrillen).

Die **Spannungs-Dehnungs-Relation** nach Hooke (linear-elastisch):

$$\\sigma = E \\cdot \\varepsilon$$

Biologische Gewebe zeigen jedoch häufig **viskoelastisches Verhalten** (Kriechverhalten,
Stress-Relaxation, frequenzabhängige Steifigkeit).

## Gelenkbiomechanik

Das Kniegelenk überträgt im Stand das 2–3-fache des Körpergewichts, beim Treppensteigen
das 3–4-fache. Implantat-Design (Endoprothesen) muss diese zyklischen Lasten über
> 10 Millionen Lastzyklen (ISO 14243) ohne Ermüdungsbruch überstehen.

## Ganganalyse und Gangzyklen

Normaler Gehzyklus: Standphase 60 %, Schwungphase 40 % des Zyklus.
**Bodenreaktionskraft (GRF)**: Charakteristischer Doppelpeak beim Gehen (~120 % BW).
Messung: Kraftplatten (piezoelektrisch oder dehnmessstreifen-basiert).

## Finite-Elemente-Methode (FEM) in der Medizintechnik

FEM wird zur Spannungsanalyse von Implantaten verwendet.
Die Gewebestruktur wird in Finite Elemente (Tetraeder, Hexaeder) diskretisiert:

$$[K]\\{u\\} = \\{F\\}$$

mit Steifigkeitsmatrix [K], Verschiebungsvektor {u}, Kraftvektor {F}.
Validierung: Experimentelle Messungen (Dehnmessstreifen, optische Verfahren).
""",
            "body_en": """\
## Mechanical Basics

Biomechanics describes mechanical properties of biological tissues and human movement.

$$\\sigma = E \\cdot \\varepsilon \\quad \\text{(Hooke's law, linear-elastic)}$$

Biological tissues exhibit **viscoelastic behaviour**: creep, stress-relaxation, frequency-
dependent stiffness.

## Tissue Mechanical Properties

| Tissue | Young's modulus E | Tensile strength |
|--------|-------------------|-----------------|
| Cortical bone | ~17 GPa | ~130 MPa |
| Cartilage | 1–10 MPa | – |
| Tendon / ligament | ~1.5 GPa | ~50–150 MPa |

## Joint Biomechanics

The knee joint bears 2–3× body weight during standing, 3–4× during stair climbing.
Implant design (total knee arthroplasty) must withstand > 10 million load cycles (ISO 14243).

## Finite Element Method (FEM)

$$[K]\\{u\\} = \\{F\\}$$

FEM is used for implant stress analysis. Validation uses strain gauges and optical methods.
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 15. Sensoren in der Medizintechnik
    # ──────────────────────────────────────────────────────────────
    "sensoren_medizin": [
        {
            "title_de": "Sensoren in der Medizintechnik",
            "title_en": "Sensors in Medical Technology",
            "body_de": """\
## Sensorklassifikation

Sensoren wandeln physikalische oder chemische Messgrößen in elektrische Signale um.
Klassifikation nach Messprinzip:

| Prinzip | Sensor-Typ | Medizinische Anwendung |
|---------|-----------|------------------------|
| Resistiv | Dehnmessstreifen, NTC/PTC | Kraftmessung, Thermometrie |
| Kapazitiv | Drucksensor, Touch | MEMS-Drucksensor, kapazitiver Touch |
| Piezoelektrisch | Quarz, PVDF | Ultraschall, Druckwellenmessung |
| Photoelektrisch | Photodiode, CCD/CMOS | Pulsoxymetrie, Endoskopie |
| Elektrochemisch | Ionenselektive Elektrode | pH, pO₂, pCO₂, Glukose |
| Induktiv / Hall | Hall-Sensor, LVDT | Positionsmessung, MRT-kompatible Sensoren |

## MEMS-Drucksensoren

Micro-Electro-Mechanical Systems (MEMS) aus Silizium werden in Katheter-Drucksensoren,
implantierbaren Drucksensoren (ICP, Augeninnendruck) und Blutdruck-Referenzwandlern
eingesetzt.

Messprinzip: Eine Silizium-Membran verbiegt sich unter Druckeinwirkung. Diffundierte
Piezoresistoren (Wheatstone-Brücke) messen die Verformung:

$$\\frac{\\Delta R}{R} = G \\cdot \\varepsilon$$

G = Gauge-Faktor (~130 für Silizium; ~2 für Metall-DMS).

## Elektrochemische Sensoren

**pH-Elektrode** (Glaselektrode): Nernst-Potenzial proportional zur H⁺-Aktivität.  
**Clark-Elektrode** (pO₂): Amperometrische Reduktion von O₂ an Platinkathode.  
**Glukosesensor** (CGM): Enzymatische Oxidation von Glukose durch GOx, amperometrische
Detektion von H₂O₂.

## Kalibrierung und Drift

Alle Sensoren unterliegen Drift (Empfindlichkeitsverlust, Offset-Verschiebung über Zeit).
Kalibrierstrategien: Zwei-Punkt-Kalibrierung, Factory-Kalibrierung + Nutzer-Trimm,
In-Vivo-Selbstkalibrierung (z. B. CGM: Sensorglukose vs. Blutglukose-Referenz).

Sensor-Leistungsparameter:
- Linearität: max. Abweichung von der idealen Geraden
- Hysterese: Messabweichung bei steigendem vs. fallendem Messwert
- Messwiederholbarkeit / Reproduzierbarkeit
""",
            "body_en": """\
## Sensor Classification

| Principle | Sensor | Medical Application |
|-----------|--------|---------------------|
| Resistive | Strain gauge, NTC/PTC | Force sensing, thermometry |
| Capacitive | MEMS pressure | Catheter pressure, touch |
| Piezoelectric | PZT, PVDF | Ultrasound, shock-wave |
| Photoelectric | Photodiode, CCD | Pulse oximetry, endoscopy |
| Electrochemical | ISE, amperometric | pH, pO₂, glucose |

## MEMS Pressure Sensors

Silicon MEMS membranes with diffused piezoresistors (Wheatstone bridge):

$$\\frac{\\Delta R}{R} = G \\cdot \\varepsilon, \\quad G \\approx 130 \\text{ (silicon)}$$

Used in catheter tips, ICP sensors, and intraocular pressure monitors.

## Electrochemical Sensors

**pH electrode**: Nernst potential proportional to H⁺ activity.  
**Clark electrode** (pO₂): Amperometric O₂ reduction at Pt cathode.  
**CGM glucose sensor**: Enzymatic GOx oxidation, H₂O₂ amperometric detection.

## Calibration and Drift

Two-point calibration, factory calibration + user trim, in-vivo self-calibration (CGM).
Key parameters: linearity, hysteresis, repeatability, reproducibility.
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 16. ISO 13485 Qualitätsmanagementsystem
    # ──────────────────────────────────────────────────────────────
    "qualitaetsmanagementsystem": [
        {
            "title_de": "Qualitätsmanagementsystem nach ISO 13485",
            "title_en": "Quality Management System per ISO 13485",
            "body_de": """\
## Einordnung und Bedeutung

**ISO 13485:2016** ist die Norm für Qualitätsmanagementsysteme (QMS) speziell für
Hersteller von Medizinprodukten. Sie ist von ISO 9001 abgeleitet, aber stärker
regulatorisch ausgerichtet (Konformität statt Kundenzufriedenheit als primäres Ziel).

**Anwendungsbereich:** Hersteller, Zulieferer, Dienstleister im Medizinprodukte-Bereich.
Zertifizierung durch akkreditierte Zertifizierungsstellen (obligatorisch für Klasse IIa–III
unter MDR).

## Kernelemente (Kapitelstruktur)

| Kapitel | Thema |
|---------|-------|
| 4 | QMS-Anforderungen (Dokumentation, Aufzeichnungen, CAPA) |
| 5 | Managementverantwortung (Qualitätspolitik, Ziele) |
| 6 | Ressourcenmanagement (Personal, Infrastruktur) |
| 7 | Produktrealisierung (Design, Beschaffung, Herstellung, Sterilisation, Messen) |
| 8 | Messung, Analyse, Verbesserung (Audit, Nonkonformität, CAPA) |

## Design und Entwicklung (7.3)

Planungs-, Eingangs-, Ausgangs-, Review-, Verifizierungs- und
Validierungsanforderungen für jede Design-Phase. Design-Freeze und
Designänderungskontrolle als kritische Qualitätstore.

## CAPA — Korrektur- und Vorbeugungsmaßnahmen

**Korrektur** (CA): Beseitigung einer bestehenden Nonkonformität.
**Vorbeugung** (PA): Verhinderung einer möglichen zukünftigen Nonkonformität.

CAPA-Prozess:
1. Problem-/Nichtkonformitätsbeschreibung
2. Ursachenanalyse (5-Why, Ishikawa, FTA)
3. Maßnahmen definieren und umsetzen
4. Effektivitätsprüfung
5. Abschluss und Dokumentation

## Interne Audits und Management-Review

Interne Audits: geplant, prozessbasiert, unabhängig (Auditor ≠ Auditierter Bereich).
Management-Review: Jährlich, mit Inputs aus Kundenfeedback, Auditberichten,
Produktqualitätsdaten, PMS-Daten, regulatorischen Änderungen.
""",
            "body_en": """\
## Overview

**ISO 13485:2016** specifies QMS requirements for medical device manufacturers, suppliers,
and service providers. It is derived from ISO 9001 but is compliance-focused rather than
customer-satisfaction-centred.

## Key Elements

| Clause | Topic |
|--------|-------|
| 4 | QMS requirements (documentation, records, CAPA) |
| 5 | Management responsibility (quality policy, objectives) |
| 6 | Resource management (personnel, infrastructure) |
| 7 | Product realisation (design, purchasing, manufacturing, sterilisation) |
| 8 | Measurement, analysis, improvement (audit, nonconformity, CAPA) |

## Design Control (7.3)

Planning → inputs → outputs → review → verification → validation for each design phase.
Design freeze and design change control are critical quality gates.

## CAPA

- **Corrective Action (CA)**: eliminate an existing nonconformity.
- **Preventive Action (PA)**: prevent a potential future nonconformity.
- Process: problem description → root cause analysis (5-Why, Ishikawa) → actions →
  effectiveness check → closure.

## Internal Audits and Management Review

Annual management review inputs: customer feedback, audit reports, product quality data,
PMS data, regulatory changes.
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 17. Sterilisationsverfahren
    # ──────────────────────────────────────────────────────────────
    "sterilisation": [
        {
            "title_de": "Sterilisationsverfahren für Medizinprodukte",
            "title_en": "Sterilisation Methods for Medical Devices",
            "body_de": """\
## Begriff und Sterilitätssicherheitsniveau (SAL)

**Sterilisation** ist die Abtötung oder Inaktivierung aller Mikroorganismen einschließlich
Sporen auf einem Produkt. Das **Sterilitätssicherheitsniveau (SAL)** gibt die
Wahrscheinlichkeit einer nicht sterilen Einheit an:

$$SAL \\leq 10^{-6} \\quad \\text{(1 nichtsteeiles Produkt pro 1 Mio. sterilisierte Produkte)}$$

## Übersicht der Sterilisationsverfahren

| Verfahren | Norm | Vorteil | Nachteil |
|-----------|------|---------|----------|
| Dampfsterilisation (Autoklav) | ISO 17665 | Günstig, effektiv | Temperaturlabil (>121°C) |
| Ethylenoxide (EtO) | ISO 11135 | Für temperatursensitive Produkte | Toxisches Restgas, Umwelt |
| Gamma-Strahlung | ISO 11137-1 | Tiefe Penetration, bulk-sterilisierung | Materialdegradation (Polycarbonat) |
| E-Beam | ISO 11137-1 | Schnell, lokale Behandlung | Geringere Penetration |
| H₂O₂-Plasma | ISO 22441 | Niedrigtemperatur, umweltfreundlich | Begrenzte Penetration |

## Bioindikatoren und chemische Indikatoren

**Bioindikatoren (BI)**: Sporenstreifen (Geobacillus stearothermophilus für Dampf/EtO;
Bacillus pumilus für Gamma-Strahlen). Nach Sterilisation: Kultivierung → kein Wachstum
→ Sterilisation validiert.

**Chemische Indikatoren (CI)**: Klasse 1–6 nach ISO 11140-1. Nur 
Prozessindikator (kein Sterilitätsnachweis).

## Validierungskonzepte

Overkill-Validierung: Startbioburden + 10⁶-Zusatzsicherheitsmarge.
Bioburden-basierte Validierung: Prozessparameter auf gemessene Produktbioburden abgestimmt.
Validierungszyklus: IQ (Installation Qualification) → OQ (Operational Qualification) →
PQ (Performance Qualification).

## Verpackung (ISO 11607)

Sterilbarriere-System muss Barriereeigenschaften bis zum Verwendungszeitpunkt
aufrechterhalten. Typisch: Tyvek®/PE-Tasche, Papier-Folie-Beutel, Tiefzieh-Blister.
Dichtigkeitsprüfung: Blaublasen-Test, Vakuum-Decay-Test.
""",
            "body_en": """\
## Sterility Assurance Level (SAL)

Sterilisation kills or inactivates all micro-organisms including spores.
Required SAL for sterile medical devices: $\\leq 10^{-6}$ (probability of a non-sterile unit).

## Methods Overview

| Method | Standard | Advantage | Disadvantage |
|--------|---------|-----------|--------------|
| Steam (autoclave) | ISO 17665 | Inexpensive, effective | Temperature-sensitive items |
| Ethylene oxide (EtO) | ISO 11135 | Temperature-sensitive items | Toxic residue, environmental |
| Gamma radiation | ISO 11137-1 | Deep penetration, bulk | Material degradation |
| H₂O₂ plasma | ISO 22441 | Low-temperature, clean | Limited penetration |

## Biological Indicators

Spore strips: Geobacillus stearothermophilus (steam/EtO); Bacillus pumilus (gamma).
Post-sterilisation culture: no growth = validated sterilisation.

## Validation

IQ → OQ → PQ. Overkill approach: bioburden + 10⁶ safety margin.

## Packaging (ISO 11607)

Sterile barrier system must maintain integrity until point of use (Tyvek®/PE pouches,
paper-foil, blister trays). Seal integrity: dye penetration, bubble emission, vacuum decay.
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 18. Elektrische Sicherheit nach IEC 60601
    # ──────────────────────────────────────────────────────────────
    "elektrische_sicherheit": [
        {
            "title_de": "Elektrische Sicherheit nach IEC 60601-1",
            "title_en": "Electrical Safety per IEC 60601-1",
            "body_de": """\
## Anwendungsbereich und Ausgaben

**IEC 60601-1:2005 + AMD1:2012 + AMD2:2020** ist die horizontale Sicherheitsnorm für
elektrische medizinische Geräte. Sie wird durch ca. 80 collateral und particular standards
(IEC 60601-2-xx) für spezifische Gerätetypen ergänzt.

## Schutzklassen

| Schutzklasse | Beschreibung | Typische Geräte |
|-------------|-------------|-----------------|
| Klasse I | Schutzleiter (PE) | Großgeräte (CT, BV-Gerät) |
| Klasse II | Schutzisolierung (doppelt/verstärkt) | Handgriffe, orale Zähne-Reiniger |
| Internal Power | Batteriebetrieben, kein Netzanschluss | Portable Monitor, Pulsoxi |

## Patientenanschluss-Typen (Applied Parts)

| Typ | Max. Patientenableitstrom (NC) | Anwendung |
|-----|-------------------------------|-----------|
| B | 500 µA | Kein direkten Herzkontakt |
| BF | 100 µA | Körperoberfläche, F = floating |
| CF | 10 µA | Direkter Herzkontakt (Katheter, EKG-Elektroden intrakardial) |

## Ableitströme und Grenzwerte

**Ableitströme** (gemessen nach IEC 60601-1):

| Ableitstromtyp | Normalbedingung | Einzelfehler |
|----------------|-----------------|--------------|
| Gehäuse-Ableitstrom | 100 µA | 500 µA |
| Patientenableitstrom (BF) | 100 µA | 500 µA |
| Patientenableitstrom (CF) | 10 µA | 50 µA |
| Netz-Patientenableitstrom | 100 µA | 1 mA (Klasse B) |

## MOOP und MOPP

**MOOP** (Means of Operator Protection): Schutz des Bedieners vor elektrischem Schlag.  
**MOPP** (Means of Patient Protection): Schutz des Patienten.  
1 MOPP: 1,5 kV Kriechwegabstand/Luftstrecke (250 V AC).  
2 MOPP: Kombination zweier unabhängiger Schutzmittel (z. B. verstärkte Isolation).

## Prüfungen nach IEC 60601-1

- Sichtprüfung: Schutzleiter, Kennzeichnung, Gebrauchsanweisung
- Elektrische Prüfung: Schutzleiterwiderstand (< 100 mΩ + 0,1 Ω/m Leitung), Ableitströme
- Spannungsfestigkeit: 1,5 kV (1 MOPP), 4 kV (2 MOPP), 60 s
- EMV: IEC 60601-1-2 (Emissionen, Störfestigkeit)
""",
            "body_en": """\
## Scope

**IEC 60601-1:2005+AMD1:2012+AMD2:2020** is the horizontal safety standard for electrical
medical equipment, complemented by ~80 collateral and particular standards.

## Protection Classes

| Class | Description | Typical Devices |
|-------|-----------|-----------------|
| Class I | Protective earth (PE) | CT, fluoroscopy |
| Class II | Double/reinforced insulation | Handheld devices |
| Internal power | Battery-operated | Portable monitors |

## Patient Connection Types (Applied Parts)

| Type | Max patient leakage (NC) | Application |
|------|--------------------------|-------------|
| B | 500 µA | No direct heart contact |
| BF | 100 µA | Body surface, floating |
| CF | 10 µA | Direct cardiac contact |

## MOOP and MOPP

**MOOP/MOPP**: means of operator/patient protection.  
2 MOPP = two independent protective means.  
Dielectric strength: 4 kV (2 MOPP), 60 s.

## Type Tests

Protective earth resistance (< 100 mΩ + cable), leakage currents, dielectric strength,
EMC per IEC 60601-1-2 (emissions and immunity).
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 19. Computertomographie (CT)
    # ──────────────────────────────────────────────────────────────
    "bildgebung_ct": [
        {
            "title_de": "Computertomographie (CT) — Grundlagen",
            "title_en": "Computed Tomography (CT) — Fundamentals",
            "body_de": """\
## Physikalisches Prinzip

Die CT misst die Schwächung von Röntgenstrahlung beim Durchgang durch Gewebe.
Das Lambert-Beer-Gesetz für polychromatische Strahlung:

$$I = I_0 \\cdot e^{-\\int \\mu(x) dx}$$

mit linearem Schwächungskoeffizient µ (HU-Skala normiert auf Wasser µ_w):

$$HU = 1000 \\cdot \\frac{\\mu - \\mu_{Wasser}}{\\mu_{Wasser} - \\mu_{Luft}}$$

| Gewebe | HU |
|--------|----|
| Luft | -1000 |
| Fett | -100 bis -50 |
| Wasser | 0 |
| Weichteil | +20 bis +80 |
| Kompaktknochen | +400 bis +1000 |

## Scanner-Geometrie und Abtastung

**Spiral-CT (Helical CT):** Röhre und Detektor rotieren kontinuierlich (Gantry-Rotation
0,27–0,5 s/U), Tisch fährt gleichzeitig. Pitch = Tischvorschub/Schichtdicke.

**Multi-Detektor-CT (MDCT):** 64–640 Detektorreihen ermöglichen isotrope Voxel
(< 0,5 mm³) und kardiale CT ohne Herzstillstand (EKG-Triggerung).

## Bildrekonstruktion

**Gefilterter Rückprojektion (FBP):** Projektionen werden mit einem Rampen-Filter
(Ram-Lak) gefaltet und zurückprojiziert:

$$f(x,y) = \\int_0^{\\pi} [p(t, \\theta) * h(t)]\\,d\\theta$$

**Iterative Rekonstruktion (IR/MBIR):** Geringere Strahlenbelastung bei gleicher
Bildqualität durch statistisches Optimierungsmodell.

## Strahlenschutz und Dosimetrie

CTDI (CT Dose Index): $CTDI_{vol} = CTDI_{100} / Pitch$  
DLP (Dose Length Product): $DLP = CTDI_{vol} \\times Scan\\,Length$  
Effektive Dosis: e = DLP × k (Konversionsfaktor nach Körperregion, ICRP 103).

Typische Dosen: Abdomen-CT ~8–10 mSv; Thorax-CT ~5–7 mSv.
Dosisreduktionsstrategien: Röhrenstrommodulation (ATCM), Low-kV-Protokolle (80 kV),
iterative Rekonstruktion, Bleiabschirmung für nicht-untersuchte Körperbereiche.

## Klinische Anwendungen

- Trauma (Polytrauma-Ganzkörper-CT)
- Onkologie (Staging, Therapiekontrolle)
- Angiographie (CTA: Aortenaneurysma, Pulmonalembolie)
- Herzdiagnostik (Koronar-CT-Angiographie, Calcium-Scoring)
- Interventionelle Planung (3D-Druck aus DICOM-Daten)
""",
            "body_en": """\
## Physics

CT measures X-ray attenuation through tissue. The Hounsfield Unit (HU) scale:

$$HU = 1000 \\cdot \\frac{\\mu - \\mu_{water}}{\\mu_{water} - \\mu_{air}}$$

| Tissue | HU |
|--------|----|
| Air | -1000 |
| Fat | -100 to -50 |
| Water | 0 |
| Soft tissue | +20 to +80 |
| Cortical bone | +400 to +1000 |

## Scanner Geometry

**Spiral CT:** Continuous gantry rotation (0.27–0.5 s/rev) and simultaneous table advance.
Pitch = table feed / slice thickness.  
**MDCT (64–640 detector rows):** Isotropic voxels < 0.5 mm³, cardiac CT with ECG gating.

## Image Reconstruction

**Filtered Back Projection (FBP):** Ram-Lak ramp filter + back-projection.  
**Iterative Reconstruction:** Lower dose at equivalent image quality.

## Radiation Dose

$CTDI_{vol}$, $DLP = CTDI_{vol} \\times scan\\_length$, effective dose E = DLP × k (ICRP 103).  
Typical: abdomen ~8–10 mSv, thorax ~5–7 mSv.  
Dose reduction: automatic tube current modulation (ATCM), low-kV protocols, iterative reconstruction.
""",
        }
    ],

    # ──────────────────────────────────────────────────────────────
    # 20. Ultraschalldiagnostik Grundlagen
    # ──────────────────────────────────────────────────────────────
    "ultraschall_grundlagen": [
        {
            "title_de": "Ultraschalldiagnostik — Physikalische Grundlagen",
            "title_en": "Diagnostic Ultrasound — Physical Fundamentals",
            "body_de": """\
## Schallphysik in biologischem Gewebe

Ultraschall (US) für medizinische Bildgebung: Frequenzbereich 1–50 MHz.
Schallgeschwindigkeit in menschlichem Gewebe:

| Gewebe | c (m/s) |
|--------|---------|
| Luft | 330 |
| Wasser | 1480 |
| Weichteil | ~1540 |
| Knochen | ~3500 |

Die verwendete mittlere Schallgeschwindigkeit in US-Geräten: **c = 1540 m/s**.

Wellenlänge: $\\lambda = c / f$. Bei f = 5 MHz → λ = 0,31 mm (axiale Auflösung ≈ λ/2).

## Reflexion und Transmission an Grenzflächen

Schalldruck-Reflexionskoeffizient an Grenzfläche aus Medium 1 und 2 (senkrechter Einfall):

$$R = \\frac{Z_2 - Z_1}{Z_2 + Z_1}, \\quad T = \\frac{2Z_2}{Z_2 + Z_1}$$

mit akustischer Impedanz $Z = \\rho \\cdot c$ [Rayl = kg/(m²·s)].

Luft/Gewebe-Grenzfläche: $R \\approx 0.9995$ (fast totale Reflexion) → Kontaktgel
zur Impedanzanpassung nötig.

## B-Mode Bildgebung (Brightness Mode)

Piezoelektrischer Wandler sendet kurze US-Pulse (Burst). Echos werden empfangen,
A-Mode-Linie (Amplitude vs. Zeit = Tiefe) aus Laufzeitmessung:

$$d = \\frac{c \\cdot t_{Laufzeit}}{2}$$

Durch Schwenken des Schallstrahls (liniar, phased array, Sektorscanner) entsteht ein 2D-Bild.

## Doppler-Sonographie

**Doppler-Effekt:** Bewegte Reflektor (Blut, Herzwand) verursacht Frequenzverschiebung:

$$\\Delta f = \\frac{2f_0 v \\cos\\theta}{c}$$

Mit $f_0$ = Sendefrequenz, v = Blutflussgeschwindigkeit, θ = Winkel Schallstrahl/Flussrichtung.

Anwendungen: Farbdoppler (CFM), Pulswellen-Doppler (PW), Continuous-Wave-Doppler (CW).

## Sicherheit: ALARA-Prinzip und MI/TI

- **Mechanischer Index (MI)**: $MI = p_{neg} / \\sqrt{f}$, Grenzwert < 1,9 (IEC 62359)
- **Thermischer Index (TI)**: TIS (Soft tissue), TIB (Bone), TIC (Cranial) — Grenzwert < 6
- **ALARA**: As Low As Reasonably Achievable — minimale US-Exposition bei ausreichender
  Bildqualität. Besonders wichtig bei fetaler Diagnostik im 1. Trimenon.
""",
            "body_en": """\
## Sound Physics in Biological Tissue

Medical diagnostic ultrasound: 1–50 MHz frequency range.
Speed of sound assumed in US scanners: **c = 1540 m/s** (soft tissue).

Wavelength: $\\lambda = c/f$. At 5 MHz → λ = 0.31 mm (axial resolution ≈ λ/2).

## Reflection at Interfaces

$$R = \\frac{Z_2 - Z_1}{Z_2 + Z_1}, \\quad Z = \\rho \\cdot c \\quad [\\text{Rayl}]$$

Air/tissue boundary: R ≈ 0.9995 → coupling gel mandatory.

## B-Mode Imaging

Piezoelectric transducer transmits short pulses. Echo depth from time-of-flight:

$$d = \\frac{c \\cdot t}{2}$$

Beam steering (linear/phased/sector array) generates a 2D image.

## Doppler Ultrasound

Frequency shift from moving reflectors (blood):

$$\\Delta f = \\frac{2f_0 v \\cos\\theta}{c}$$

Applications: colour flow mapping (CFM), pulsed-wave (PW), continuous-wave (CW) Doppler.

## Safety: MI/TI and ALARA

- **Mechanical Index (MI)**: $MI = p_{neg}/\\sqrt{f}$, threshold < 1.9 (IEC 62359)
- **Thermal Index (TI)**: TIS / TIB / TIC — threshold < 6
- **ALARA principle**: minimum exposure for adequate image quality (critical for
  first-trimester fetal imaging).
""",
        }
    ],
}

