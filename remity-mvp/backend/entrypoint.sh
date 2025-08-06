#!/bin/sh

# Run database migrations
alembic upgrade head

# Start Uvicorn server
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
