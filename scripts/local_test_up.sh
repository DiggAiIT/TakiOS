#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/.logs"
RUN_DIR="$ROOT_DIR/.run"

mkdir -p "$LOG_DIR" "$RUN_DIR"

ensure_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

wait_for_http() {
  local url="$1"
  local label="$2"
  local retries="${3:-40}"
  local sleep_seconds="${4:-1}"

  for _ in $(seq 1 "$retries"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "$label is ready: $url"
      return 0
    fi
    sleep "$sleep_seconds"
  done

  echo "$label did not become ready in time: $url" >&2
  return 1
}

start_docker_daemon_if_needed() {
  if docker info >/dev/null 2>&1; then
    return 0
  fi

  if command -v colima >/dev/null 2>&1; then
    echo "Docker daemon not reachable, starting Colima..."
    colima start
  elif [[ "$(uname -s)" == "Darwin" ]]; then
    echo "Docker daemon not reachable, trying Docker Desktop..."
    open -a Docker || true
  fi

  for _ in $(seq 1 40); do
    if docker info >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done

  echo "Docker daemon is not available. Start Colima or Docker Desktop and retry." >&2
  exit 1
}

start_or_replace_container() {
  local name="$1"
  shift

  docker rm -f "$name" >/dev/null 2>&1 || true
  docker run -d --name "$name" "$@" >/dev/null
  echo "Started container: $name"
}

start_backend() {
  local pid_file="$RUN_DIR/backend.pid"

  if curl -fsS "http://localhost:8000/health" >/dev/null 2>&1; then
    echo "Backend already reachable on :8000; skipping local start."
    return 0
  fi

  if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" >/dev/null 2>&1; then
    echo "Backend already running (pid $(cat "$pid_file"))."
    return 0
  fi

  echo "Starting backend on :8000..."
  (
    cd "$ROOT_DIR/backend"
    exec "$ROOT_DIR/.venv/bin/uvicorn" app.main:app --reload --host 0.0.0.0 --port 8000
  ) >"$LOG_DIR/backend.log" 2>&1 &

  echo $! >"$pid_file"
}

start_frontend() {
  local pid_file="$RUN_DIR/frontend.pid"

  if curl -fsS "http://localhost:3000/de" >/dev/null 2>&1; then
    echo "Frontend already reachable on :3000; skipping local start."
    return 0
  fi

  if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" >/dev/null 2>&1; then
    echo "Frontend already running (pid $(cat "$pid_file"))."
    return 0
  fi

  echo "Starting frontend on :3000..."
  (
    cd "$ROOT_DIR/frontend"
    exec npm run dev -- --hostname 0.0.0.0 --port 3000
  ) >"$LOG_DIR/frontend.log" 2>&1 &

  echo $! >"$pid_file"
}

main() {
  ensure_cmd docker
  ensure_cmd curl

  start_docker_daemon_if_needed

  docker network inspect takios-dev >/dev/null 2>&1 || docker network create takios-dev >/dev/null

  start_or_replace_container takios-postgres \
    --network takios-dev \
    -e POSTGRES_USER=takios \
    -e POSTGRES_PASSWORD=takios \
    -e POSTGRES_DB=takios \
    -p 5432:5432 \
    pgvector/pgvector:pg16

  start_or_replace_container takios-redis \
    --network takios-dev \
    -p 6379:6379 \
    redis:7-alpine

  start_or_replace_container takios-minio \
    --network takios-dev \
    -e MINIO_ROOT_USER=minioadmin \
    -e MINIO_ROOT_PASSWORD=minioadmin \
    -p 9000:9000 \
    -p 9001:9001 \
    minio/minio server /data --console-address :9001

  echo "Running migrations..."
  (
    cd "$ROOT_DIR/backend"
    "$ROOT_DIR/.venv/bin/alembic" upgrade head
  )

  start_backend
  start_frontend

  wait_for_http "http://localhost:8000/health" "Backend"
  wait_for_http "http://localhost:3000/de" "Frontend"

  echo
  echo "Local test stack is ready."
  echo "Frontend: http://localhost:3000/de"
  echo "Backend:  http://localhost:8000/health"
  echo "MinIO:    http://localhost:9001"
  echo "Logs:     $LOG_DIR"
}

main "$@"
