# TakiOS

TakiOS ist eine Full-Stack-Lernplattform mit FastAPI-Backend und Next.js-Frontend.

## Status

- Frontend-Datenfluss ist in den zentralen Produktbereichen auf React Query umgestellt
- Backend-Routentests decken Projects, Quality, Compliance, Collaboration und Impact ab
- Standard-Local-Stack laeuft ueber die Infrastruktur-Compose-Datei

## Struktur

- `backend`: FastAPI API, Layer-Architektur, SQLAlchemy, Alembic
- `frontend`: Next.js App Router, next-intl, React Query, Tailwind
- `infrastructure`: Dockerfiles und Compose-Stack fuer lokale Infrastruktur
- `scripts`: Hilfsskripte fuer Seed-Daten

## Lokaler Start

1. Setup ausfuehren:

   ```bash
   ./setup.sh
   ```

2. Umgebungsvariablen pruefen:

   - Root: `.env`
   - Frontend: `frontend/.env` wird bei vorhandenem Beispiel automatisch aus `frontend/.env.example` erzeugt
   - Fuer Next-Rewrites wird zusaetzlich `NEXT_INTERNAL_API_URL` verwendet; lokal darf das auf `http://localhost:8000/api/v1` bleiben
   - `SEED_DATA=1` aktiviert optional das automatische Laden der Seed-Daten im Container-Start

3. Datenbankmigration nach dem Start der Datenbank ausfuehren:

   ```bash
   cd backend && source .venv/bin/activate && alembic upgrade head
   ```

4. Infrastruktur starten:

   ```bash
   docker compose -f infrastructure/docker-compose.yml up --build
   ```

   Hinweis:
   - Diese Datei ist der empfohlene Compose-Einstieg fuer lokale Entwicklung.
   - Dafuer wird eine Compose-faehige CLI benoetigt, also entweder `docker compose` oder `docker-compose`.
   - Die Root-Datei `docker-compose.yml` ist nur eine alternative/legacy Variante. Fuer den dokumentierten Dev-Flow sollte `infrastructure/docker-compose.yml` verwendet werden.
   - Die Infrastruktur-Compose-Datei erzwingt intern die Service-Hosts `postgres`, `redis`, `minio` und `backend`, damit Container nicht versehentlich gegen `localhost` verbinden.
   - Der Backend-Container nutzt seinen EntryPoint fuer `alembic upgrade head`; Migrationen laufen dort vor dem API-Start automatisch.

5. Alternativ lokal getrennt starten:

   ```bash
   cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   ```bash
   cd frontend && npm run dev
   ```

## Autonomer Local-Test-Workflow

Wenn `docker compose` lokal fehlt, kann der gesamte Test-Stack autonom mit den
neuen Helper-Skripten gestartet werden:

```bash
make local-test-up
```

Status anzeigen:

```bash
make local-test-status
```

Stack stoppen:

```bash
make local-test-down
```

Der Workflow startet automatisch (falls noetig) den Docker-Daemon, startet
PostgreSQL/Redis/MinIO, fuehrt `alembic upgrade head` aus und startet Backend
und Frontend mit Log-Ausgabe unter `.logs/`.

## Tests

- Backend:

   ```bash
   cd backend && pytest
   ```

- Frontend Typpruefung:

   ```bash
   cd frontend && npx tsc --noEmit
   ```

- Frontend Build:

   ```bash
   cd frontend && npm run build
   ```

## Wichtige Pfade

- API Einstieg: `backend/app/main.py`
- Frontend Einstieg: `frontend/src/app/[locale]`
- API Client: `frontend/src/lib/api-client.ts`

## Weitere Doku

- [backend/README.md](backend/README.md)
- [frontend/README.md](frontend/README.md)
- [infrastructure/README.md](infrastructure/README.md)

Die Detaildokumentation fuer Setup, Entwicklung und Infrastruktur liegt in den jeweiligen Unterverzeichnissen.
