# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Set PATH to include local bin directory for installed packages like alembic
ENV PATH="/root/.local/bin:${PATH}"

# Set work directory
WORKDIR /app

# Install system dependencies needed for psycopg2 build and pg_isready
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    postgresql-client \
    build-essential libpq-dev \
    dos2unix \
    # Clean up apt cache to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy requirements next to leverage cache if requirements haven't changed
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# entrypoint.sh is no longer used, logic moved to docker-compose command

# Expose the port the app runs on
EXPOSE 8000

# Default command (will be overridden by docker-compose command)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
