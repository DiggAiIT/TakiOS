# TakiOS Backend

## Stack

- FastAPI
- SQLAlchemy Async
- Alembic
- PostgreSQL mit pgvector
- Redis / Celery
- MinIO

## Einstieg

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Start

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Migrationen

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

## Tests

```bash
cd backend
pytest
```

## Struktur

- `app/api`: API-Router und Entry-Points
- `app/layers`: Fachliche Layer L01 bis L13
- `app/services`: zentrale Services ausserhalb der Layer
- `app/core`: Auth, Storage, Events, AI-Grundbausteine
- `tests`: API- und Sicherheits-Regressionstests

## Relevante Dateien

- `app/main.py`: FastAPI-App, Middleware, globale Fehlerbehandlung
- `app/api/api.py`: Router-Montage unter `/api/v1`
- `pyproject.toml`: Python-Paket, Dev-Dependencies, pytest-Konfiguration
