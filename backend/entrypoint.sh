#!/bin/sh

set -eu

eval "$(python3 - <<'PY'
import os
from urllib.parse import urlparse

database_url = os.environ.get("DATABASE_URL", "")
if not database_url or database_url.startswith("sqlite"):
    raise SystemExit(0)

normalized = database_url.replace("postgresql+asyncpg", "postgresql", 1)
parsed = urlparse(normalized)

for key, value in {
    'PGHOST': parsed.hostname or 'postgres',
    'PGPORT': str(parsed.port or 5432),
    'PGUSER': parsed.username or 'takios',
    'PGDATABASE': (parsed.path or '/takios').lstrip('/'),
}.items():
    print(f"export {key}='{value}'")
PY
)"

if [ -n "${PGHOST:-}" ]; then
  tries=0
  until pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" >/dev/null 2>&1; do
    tries=$((tries + 1))
    if [ "$tries" -ge 30 ]; then
      echo "Database did not become ready in time" >&2
      exit 1
    fi
    sleep 1
  done
fi

alembic upgrade head

if [ "${SEED_DATA:-0}" = "1" ]; then
  python3 -m app.data.seed_curriculum || true
  python3 -m app.data.seed_content || true
fi

exec "$@"