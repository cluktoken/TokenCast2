#!/usr/bin/env bash
set -euo pipefail

echo "Waiting for PostgreSQL..."
python - <<'PY'
import os, time
import sqlalchemy as sa
url = os.environ.get("DATABASE_URL", "postgresql+psycopg2://tokencast:tokencast@db:5432/tokencast")
engine = sa.create_engine(url, pool_pre_ping=True)
for attempt in range(60):
    try:
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
        print("Database is ready.")
        break
    except Exception as exc:
        print(f"  db not ready ({attempt+1}/60): {exc}")
        time.sleep(2)
else:
    raise SystemExit("Database did not become ready in time.")
PY

echo "Running database migrations..."
alembic upgrade head

echo "Starting TokenCast API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers
