# Globale Architektur- und Sicherheitsrichtlinien (ISO/IEC 42001 & EU AI Act Compliance)

> **Scope:** Dieses Dokument gilt für alle Copilot-Generierungen im TakiOS-Workspace.
> Es definiert verbindliche Leitplanken für Security-by-Design, Traceability und
> Zuständigkeitstrennung gemäß ISO/IEC 42001, EU AI Act (Art. 11/12) und BSI TR-03161.

## 1. Technologiestack & Sicherheit (BSI Guidelines)

### Backend (Python)
* Framework: **FastAPI** mit async/await durchgängig bis zur Datenbankschicht.
* ORM: **SQLAlchemy 2** (async), Migrationen via **Alembic**.
* Alle neuen Models MÜSSEN von `app.shared.base_model.AuditBase` erben (UUID-PK, `created_at`, `updated_at`).
* Passwörter: Ausschließlich **bcrypt** via `passlib`. Kein Klartext, kein MD5/SHA.
* API-Keys und Secrets: NUR über Umgebungsvariablen (`app.config.settings`), niemals hardcoded.
* Shell-Aufrufe: **Verboten** in Backend-Code. Kein `subprocess`, kein `os.system()`. Falls zwingend nötig: nur `subprocess.run()` mit expliziter Argument-Liste (kein `shell=True`).
* Input-Validierung: Alle API-Eingaben über **Pydantic v2** Schemas validieren. Niemals rohe Request-Bodies verarbeiten.
* SQL: Ausschließlich SQLAlchemy Query-Builder oder ORM. Kein Raw-SQL mit String-Interpolation.

### Frontend (TypeScript)
* Framework: **Next.js 15** mit App Router und `[locale]`-Routing.
* State: **Zustand** (Client), **TanStack Query** (Server-State).
* i18n: **next-intl** mit statischen JSON-Message-Dateien unter `messages/`.
* Keine `dangerouslySetInnerHTML` ohne vorherige Sanitisierung.
* API-Calls: Ausschließlich über typisierte Fetch-Wrapper mit Zod-Validierung der Responses.

### Standalone Orchestrator (Node.js)
* Alle ausführbaren Kernmodule im Ordner `bin/lib/` MÜSSEN im **CommonJS-Format** (`.cjs`) geschrieben sein. Nutze `require()`, keine ESM Imports.
* Vermeide externe Abhängigkeiten, wo immer möglich. Nutze Node.js Built-ins.
* Führe niemals Shell-Befehle über `execSync` mit String-Interpolation aus. Nutze ausschließlich `execFileSync` mit Arrays.
* Der Orchestrator kommuniziert mit dem Backend ausschließlich über die REST-API (`/api/v1/`).

## 2. Agenten-Definition & Orchestrierung

### VS Code Agent-Definitionen (Option B)
* Copilot-Agenten werden als `.agent.md`-Dateien im Ordner `.github/agents/` definiert.
* Jeder Agent hat YAML-Frontmatter mit `name`, `description` und optionalen `tools`-Restrictions.
* Agenten nutzen das bestehende Multi-Model-Routing aus `app.core.ai.router`:
  - **Opus**: NUR für komplexe Planungsphasen (Token-Entropie minimieren)
  - **Sonnet**: Standard-Ausführung
  - **Haiku**: Synthese und leichte Aufgaben

### Standalone Agent-Definitionen (Option C)
* Agenten werden als Markdown-Dateien (`.md`) im Ordner `agents/` definiert.
* Die Engine in `bin/lib/motor.cjs` parst diese Definitionen zur Laufzeit.
* Kontext-Hygiene: Das "AutoDream"-System komprimiert Memory-Einträge periodisch (12h-Intervall, 50-Session-Schwellwert) zu kompakten Index-Einträgen (max 200 Zeilen, je 120 Zeichen).

## 3. Lückenloses Logging (EU AI Act Art. 12 – Traceability)

* **Jede KI-Entscheidung** (Grading, Mnemonic-Generierung, Projektanalyse) MUSS protokolliert werden mit:
  - Timestamp (UTC, timezone-aware)
  - Request-ID (UUID, via `X-Request-Id`-Header)
  - Verwendetes Modell und Routing-Profil
  - Input-Token-Schätzung und Output-Token-Schätzung
  - Ergebnis-Kategorie (z.B. Score, Klassifikation)
* Die `AuditLogMiddleware` loggt alle zustandsverändernden Requests.
* Compliance-Evidenzen werden in Layer 11 (`ComplianceEvidence`) mit Prüfer-UUID und Prüfdatum persistiert.
* Memory-Konsolidierung (AutoDream) protokolliert: Zyklus-Nummer, verarbeitete Sessions, Index-Zeilen vorher/nachher.

## 4. Datenschutz (DSGVO / BSI TR-03161)

* Keine personenbezogenen Daten in Log-Ausgaben (keine E-Mails, keine Klarnamen).
* User-Identifikation in Logs ausschließlich über UUIDs.
* Alle Zeitstempel timezone-aware (UTC).
* Content-Versionierung: Append-only (`ContentVersion`-Tabelle), niemals Inhalte überschreiben.
* Löschrecht: Implementiere Soft-Delete mit `status`-Flag, Hard-Delete nur über dedizierte Admin-Endpoints.

## 5. Architektur-Invarianten

* **13-Layer-Modell**: Neue Features MÜSSEN in den passenden Layer (L01–L13) eingeordnet werden.
* **EventBus**: Cross-Layer-Kommunikation NUR über `app.core.events.EventBus`. Kein direkter Import zwischen Layern.
* **Keine zirkulären Imports**: Layer dürfen nur `shared/`, `core/` und `config` importieren, nicht andere Layer.
* **Bilingualität**: Alle inhaltlichen Felder MÜSSEN `_de`- und `_en`-Varianten haben.
* **Tests**: Jede neue Funktion braucht mindestens einen Unit-Test in `tests/`.
