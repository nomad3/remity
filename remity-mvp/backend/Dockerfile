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
    # for pg_isready:
    postgresql-client \
    # for psycopg2 build from source (if needed, though binary should work):
    build-essential libpq-dev \
    # Clean up apt cache to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
# Install dependencies, including dev dependencies like alembic needed for entrypoint
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script and make it executable
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the entrypoint script by default
ENTRYPOINT ["/app/entrypoint.sh"]
# Default command (will be executed by entrypoint.sh if provided)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
