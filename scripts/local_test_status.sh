#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT_DIR/.run"

show_pid_status() {
  local name="$1"
  local pid_file="$RUN_DIR/$name.pid"
  local external_url=""

  if [[ "$name" == "backend" ]]; then
    external_url="http://localhost:8000/health"
  elif [[ "$name" == "frontend" ]]; then
    external_url="http://localhost:3000/de"
  fi

  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" >/dev/null 2>&1; then
      echo "$name: running (pid $pid)"
      return
    fi
  fi

  if [[ -n "$external_url" ]] && curl -fsS "$external_url" >/dev/null 2>&1; then
    echo "$name: running (external process, no pid file)"
    return
  fi

  echo "$name: not running"
}

show_http_status() {
  local label="$1"
  local url="$2"

  if curl -fsS "$url" >/dev/null 2>&1; then
    echo "$label: reachable ($url)"
  else
    echo "$label: unreachable ($url)"
  fi
}

main() {
  show_pid_status backend
  show_pid_status frontend

  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "NAMES|takios-postgres|takios-redis|takios-minio" || true
  else
    echo "docker: daemon unavailable"
  fi

  show_http_status backend "http://localhost:8000/health"
  show_http_status frontend "http://localhost:3000/de"
}

main "$@"
