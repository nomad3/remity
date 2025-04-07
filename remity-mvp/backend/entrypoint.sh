#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for the database to be ready
# Use environment variables defined in docker-compose.yml
echo "Waiting for database at ${POSTGRES_HOST}:${POSTGRES_PORT}..."

# Function to check DB readiness
check_db() {
    pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -q
}

# Wait for the DB server itself to be ready first (without specifying DB name)
while ! pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -q; do
  echo "PostgreSQL server is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL server is up."

# Check if the specific database exists and is ready
if ! check_db; then
    echo "Database '${POSTGRES_DB}' not found or not ready. Attempting to create..."
    # Use PGPASSWORD for createdb if user has password authentication configured
    export PGPASSWORD="${POSTGRES_PASSWORD}"
    # Attempt creation - script will exit if this fails and DB doesn't exist
    createdb -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" "${POSTGRES_DB}"
    echo "Database creation command executed (or database already existed)."
    unset PGPASSWORD

    # Add a small delay after creation attempt before checking again
    sleep 2

    # Wait again specifically for the database after attempting creation
    echo "Waiting for database '${POSTGRES_DB}' to become ready after creation attempt..."
    while ! check_db; do
      echo "Database '${POSTGRES_DB}' is still unavailable - sleeping"
      sleep 1
    done
fi

echo "Database '${POSTGRES_DB}' is ready - executing command"

# Apply database migrations
echo "Applying database migrations..."
# Ensure alembic can find the config relative to the app directory
# The working directory is /app as set in the Dockerfile
alembic -c /app/alembic.ini upgrade head

echo "Migrations applied."

# Execute the main container command (passed as arguments to this script)
echo "Starting application: exec $@"
exec "$@"
