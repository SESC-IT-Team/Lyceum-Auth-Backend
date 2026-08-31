#!/bin/bash
set -e
echo "Running database migrations..."
echo "${POSTGRES_HOST}"

uv run --no-sync alembic upgrade head
if [ $? -ne 0 ]; then
  echo "Migration failed. Exiting."
  exit 1
fi
echo "Migrations completed successfully."

echo "Starting application..."
exec uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port 8000
