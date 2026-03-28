# TakiOS Infrastruktur

## Empfohlener Compose-Start

```bash
docker compose -f infrastructure/docker-compose.yml up --build
```

Diese Datei ist der empfohlene lokale Dev-Entry-Point.

Wenn lokal sowohl `docker compose` als auch `docker-compose` unterschiedlich verfuegbar sind, sollte bevorzugt die Compose-v2-Variante `docker compose` verwendet werden.
Mindestens eine dieser beiden Compose-Varianten muss installiert sein.

## Enthaltene Services

- `postgres`: PostgreSQL mit pgvector
- `redis`: Cache und Task-Queue-Basis
- `minio`: S3-kompatibler Storage
- `backend`: FastAPI-Container
- `frontend`: Next.js-Container

## Dockerfiles

- `Dockerfile.backend`: baut das Python-Backend direkt aus `backend/`
- `Dockerfile.frontend`: baut das Next.js-Frontend aus `frontend/`

## Hinweise

- Root-`docker-compose.yml` und `infrastructure/docker-compose.yml` sind beide vorhanden.
- Fuer lokale Entwicklung sollte bevorzugt `infrastructure/docker-compose.yml` genutzt werden.
- Die Root-Datei ist nicht der primäre dokumentierte Dev-Flow.
- Die Compose-Datei setzt fuer Container-interne Abhaengigkeiten feste Service-Ziele statt `localhost`:
  - Backend -> `postgres`, `redis`, `minio`
  - Frontend-Rewrites -> `NEXT_INTERNAL_API_URL=http://backend:8000/api/v1`
- Der Backend-Container startet ueber `backend/entrypoint.sh`; dadurch laufen Migrationen automatisch vor `uvicorn`.
- Optional kann ueber `SEED_DATA=1` Seed-Datenmaterial beim Containerstart geladen werden.
- Nach erstem Datenbankstart die Migration separat ausfuehren:

  ```bash
  cd backend && source .venv/bin/activate && alembic upgrade head
  ```
