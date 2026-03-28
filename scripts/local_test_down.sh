#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT_DIR/.run"

stop_pid() {
  local name="$1"
  local pid_file="$RUN_DIR/$name.pid"

  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
      sleep 1
      if kill -0 "$pid" >/dev/null 2>&1; then
        kill -9 "$pid" >/dev/null 2>&1 || true
      fi
      echo "Stopped $name (pid $pid)."
    fi
    rm -f "$pid_file"
  else
    echo "$name not started by local_test_up.sh (no pid file)."
  fi
}

remove_container() {
  local name="$1"
  if command -v docker >/dev/null 2>&1; then
    docker rm -f "$name" >/dev/null 2>&1 || true
    echo "Stopped container: $name"
  fi
}

main() {
  stop_pid backend
  stop_pid frontend

  remove_container takios-minio
  remove_container takios-redis
  remove_container takios-postgres

  echo "Local test stack stopped."
}

main "$@"
