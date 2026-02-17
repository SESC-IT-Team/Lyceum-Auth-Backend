#!/bin/sh
set -e

echo "Running database migrations..."
uv run alembic upgrade head
if [ $? -ne 0 ]; then
    echo "Migration failed. Exiting."
    exit 1
fi
echo "Migrations completed successfully."

echo "Starting application..."
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
