#!/bin/bash
# Basic entrypoint script

echo "Entrypoint script started..."

# Wait for the database to be ready
echo "Waiting for database at ${POSTGRES_HOST}:${POSTGRES_PORT}..."

# Function to check DB readiness
check_db() {
    pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -q
}

# Wait for the DB server itself
while ! pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -q; do
  echo "PostgreSQL server is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL server is up."

# Check/Create/Wait for specific DB
if ! check_db; then
    echo "Database '${POSTGRES_DB}' not found or not ready. Attempting to create..."
    export PGPASSWORD="${POSTGRES_PASSWORD}"
    createdb -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" "${POSTGRES_DB}"
    echo "Database creation command executed (or database already existed)."
    unset PGPASSWORD
    sleep 2
    echo "Waiting for database '${POSTGRES_DB}' to become ready after creation attempt..."
    while ! check_db; do
      echo "Database '${POSTGRES_DB}' is still unavailable - sleeping"
      sleep 1
    done
fi
echo "Database '${POSTGRES_DB}' is ready."

# Apply database migrations
# Check if the users table exists
echo "Checking if the users table exists..."
PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -tAc "SELECT 1 FROM pg_tables WHERE tablename='users'" | grep -q 1
if [ $? -eq 0 ]; then
  echo "Users table exists."
else
  echo "Users table does not exist. Applying database migrations..."
  alembic -c /app/alembic.ini upgrade head
  echo "Migrations applied."
fi

# Run initial data script
echo "Running initial data script..."
python -m app.initial_data --email admin@remity.io --password simon144610
echo "Initial data script completed."

# Execute the main container command
echo "Starting application: exec $@"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
