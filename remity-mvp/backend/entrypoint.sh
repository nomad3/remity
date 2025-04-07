#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for the database to be ready
# Use environment variables defined in docker-compose.yml
echo "Waiting for database at ${POSTGRES_HOST}:${POSTGRES_PORT}..."

# Loop until pg_isready returns success (0)
# Requires postgresql-client to be installed in the Docker image
while ! pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -q; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database is up - executing command"

# Apply database migrations
echo "Applying database migrations..."
# Ensure alembic can find the config relative to the app directory
# The working directory is /app as set in the Dockerfile
alembic -c /app/alembic.ini upgrade head

echo "Migrations applied."

# Execute the main container command (passed as arguments to this script)
echo "Starting application: exec $@"
exec "$@"
