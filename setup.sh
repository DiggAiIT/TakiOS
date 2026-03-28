#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

echo "Preparing TakiOS workspace..."

if [[ ! -f "$ROOT_DIR/.env" && -f "$ROOT_DIR/.env.example" ]]; then
	cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
	echo "Created .env from .env.example"
fi

if [[ ! -f "$FRONTEND_DIR/.env" && -f "$FRONTEND_DIR/.env.example" ]]; then
	cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env"
	echo "Created frontend/.env from frontend/.env.example"
fi

echo "Installing Backend Dependencies..."
cd "$BACKEND_DIR"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

echo "======================================"

echo "Installing Frontend Dependencies..."
cd "$FRONTEND_DIR"
npm install

echo "======================================"
echo "Setup complete! Review .env in the repo root before starting services."
echo "Local backend flow: cd backend && source .venv/bin/activate && alembic upgrade head"
echo "Local backend flow: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "Local frontend flow: cd frontend && npm run dev"
echo "Container flow: docker compose -f infrastructure/docker-compose.yml up --build"
echo "Container flow note: backend entrypoint runs alembic upgrade head automatically before uvicorn starts"
echo "Container flow note: set SEED_DATA=1 in .env if curriculum/content seed data should be loaded on startup"
